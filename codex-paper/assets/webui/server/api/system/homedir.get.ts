import { homedir } from 'os'

export default defineEventHandler(() => {
  const libraryRoot = process.env.CODEX_PAPER_LIBRARY || `${homedir()}/codex-papers`
  return {
    homedir: homedir(),
    libraryRoot
  }
})
