import fs from 'fs';
import pdf from 'pdf-parse';

const pdfPath = process.argv[2];
if (!pdfPath) {
  console.error('Usage: node parse-pdf.js <pdf-path>');
  process.exit(1);
}

// Wrap in async IIFE to handle async/await properly
(async () => {
  const dataBuffer = fs.readFileSync(pdfPath);
  const data = await pdf(dataBuffer);

  const lines = data.text.split('\n').map(l => l.trim()).filter(Boolean);

  function looksLikeBadTitle(line) {
    const low = line.toLowerCase();
    return (
      low.includes('provided proper attribution') ||
      low.includes('google hereby grants permission') ||
      low.includes('permission to use') ||
      low.includes('copyright') ||
      low.includes('arxiv:') ||
      low.startsWith('accepted at') ||
      low.startsWith('published as') ||
      low.includes('journalistic or') ||
      low.includes('scholarly works') ||
      line.length > 180
    );
  }

  function titleScore(line) {
    const words = line.split(/\s+/).filter(Boolean);
    const alphaWords = words.filter(word => /[A-Za-z]/.test(word));
    const titleishWords = alphaWords.filter(word => /^[A-Z][A-Za-z'’-]*$/.test(word));
    const hasTerminalPunctuation = /[.,;:]$/.test(line);
    const startsLower = /^[a-z]/.test(line);
    const hasEmail = /@/.test(line);

    let score = 0;
    score += Math.min(alphaWords.length, 12);
    score += titleishWords.length * 3;
    if (words.length >= 3 && words.length <= 12) score += 8;
    if (!hasTerminalPunctuation) score += 5;
    if (!startsLower) score += 8;
    if (hasEmail) score -= 20;
    if (line.length > 120) score -= 10;
    if (/^[\W\d]+$/.test(line)) score -= 20;
    return score;
  }

  function pickTitle() {
    const infoTitle = data?.info?.Title?.trim();
    if (infoTitle && !looksLikeBadTitle(infoTitle) && infoTitle.toLowerCase() !== 'untitled') {
      return infoTitle;
    }

    const candidates = lines
      .slice(0, 20)
      .filter(line => line.length >= 10 && line.length <= 180)
      .filter(line => !looksLikeBadTitle(line))
      .filter(line => !/^[\d\W]+$/.test(line))
      .filter(line => !/@/.test(line))
      .map(line => ({ line, score: titleScore(line) }))
      .sort((a, b) => b.score - a.score);

    return candidates[0]?.line || 'Untitled';
  }

  const title = pickTitle();

  // Extract abstract
  const abstractMatch = data.text.match(/Abstract\s+(.+?)\s+(?=1\. Introduction|Introduction|$)/is);
  const abstract = abstractMatch ? abstractMatch[1].trim() : '';

  // Detect GitHub URLs
  const githubMatch = data.text.match(/https?:\/\/github\.com\/[^\s\)]+/g);
  const githubLinks = githubMatch || [];

  // Detect other code links (arXiv, CodeOcean, etc.)
  const codeUrlPatterns = [
    /https?:\/\/(?:www\.)?arxiv\.org\/(?:code|src)\/[^\s\)]+/gi,
    /https?:\/\/(?:www\.)?codeocean\.com\/[^\s\)]+/gi,
    /https?:\/\/(?:www\.)?openreview\.net\/code[^\s\)]+/gi,
    /https?:\/\/(?:www\.)?paperswithcode\.com\/[^\s\)]+/gi,
    /\[code[\^\]]*\]\(https?:\/\/[^\)]+\)/gi
  ];

  const codeLinks = [];
  for (const pattern of codeUrlPatterns) {
    const matches = data.text.match(pattern);
    if (matches) {
      codeLinks.push(...matches.filter(l => !githubLinks.includes(l)));
    }
  }

  function looksLikeAuthorLine(line) {
    if (!line || line.length < 3 || line.length > 60) return false;
    if (/@/.test(line)) return false;
    if (/abstract/i.test(line)) return false;
    if (/google|university|institute|research|laboratory|school|department/i.test(line)) return false;
    if (!/[A-Za-z]/.test(line)) return false;

    const cleaned = line.replace(/[∗†‡*]/g, '').trim();
    if (!cleaned) return false;
    const words = cleaned.split(/\s+/).filter(Boolean);
    if (words.length < 2 || words.length > 4) return false;

    return words.every(word => /^[A-ZÀ-ÖØ-ÞŁ][A-Za-zÀ-ÖØ-öø-ÿŁł.'’-]*$/.test(word));
  }

  const authors = [];
  for (const line of lines.slice(0, 35)) {
    if (/^abstract$/i.test(line)) break;
    if (looksLikeAuthorLine(line)) {
      const cleaned = line.replace(/[∗†‡*]/g, '').trim();
      if (!authors.includes(cleaned)) {
        authors.push(cleaned);
      }
    }
  }

  // Truncate content if too large (max 50000 chars to prevent token issues)
  const MAX_CONTENT_LENGTH = 50000;
  const truncatedContent = data.text.length > MAX_CONTENT_LENGTH
    ? data.text.substring(0, MAX_CONTENT_LENGTH) + '... [content truncated]'
    : data.text;

  const metadata = {
    title,
    authors,
    abstract,
    content: truncatedContent,
    githubLinks,
    codeLinks: [...new Set(codeLinks)], // Remove duplicates
    pageCount: data.numpages
  };

  console.log(JSON.stringify(metadata, null, 2));
})().catch(err => {
  console.error('Error parsing PDF:', err);
  process.exit(1);
});
