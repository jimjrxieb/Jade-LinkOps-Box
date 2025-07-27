/**
 * Maps file extensions to their corresponding icons
 * @param {string} filename - The filename or path to get an icon for
 * @returns {string} An emoji icon representing the file type
 */
export function getFileIcon(filename) {
  if (!filename) return '❔'
  
  const ext = filename.toLowerCase().split('.').pop()
  
  // Tool/Config files
  if (['json', 'yaml', 'yml', 'toml'].includes(ext)) return '🛠️'
  
  // Data files
  if (['csv', 'xlsx', 'xls', 'tsv'].includes(ext)) return '📊'
  
  // Document files
  if (['txt', 'md', 'rst', 'adoc'].includes(ext)) return '📄'
  if (['pdf', 'doc', 'docx'].includes(ext)) return '📕'
  
  // Code files
  if (['py', 'js', 'ts', 'jsx', 'tsx'].includes(ext)) return '💻'
  if (['sh', 'bash', 'zsh', 'fish'].includes(ext)) return '⚡'
  
  // Image files
  if (['jpg', 'jpeg', 'png', 'gif', 'svg'].includes(ext)) return '🖼️'
  
  // Archive files
  if (['zip', 'tar', 'gz', 'rar', '7z'].includes(ext)) return '📦'
  
  // Unknown
  return '❔'
}

/**
 * Gets a human-readable file type description
 * @param {string} filename - The filename or path
 * @returns {string} A description of the file type
 */
export function getFileTypeDescription(filename) {
  if (!filename) return 'Unknown File'
  
  const ext = filename.toLowerCase().split('.').pop()
  
  // Tool/Config files
  if (['json', 'yaml', 'yml', 'toml'].includes(ext)) return 'Configuration File'
  
  // Data files
  if (['csv', 'xlsx', 'xls'].includes(ext)) return 'Spreadsheet'
  if (['tsv'].includes(ext)) return 'Tab-Separated Data'
  
  // Document files
  if (['txt'].includes(ext)) return 'Text Document'
  if (['md', 'rst', 'adoc'].includes(ext)) return 'Documentation'
  if (['pdf'].includes(ext)) return 'PDF Document'
  if (['doc', 'docx'].includes(ext)) return 'Word Document'
  
  // Code files
  if (['py'].includes(ext)) return 'Python Script'
  if (['js'].includes(ext)) return 'JavaScript File'
  if (['ts'].includes(ext)) return 'TypeScript File'
  if (['jsx', 'tsx'].includes(ext)) return 'React Component'
  if (['sh', 'bash', 'zsh', 'fish'].includes(ext)) return 'Shell Script'
  
  // Image files
  if (['jpg', 'jpeg', 'png', 'gif', 'svg'].includes(ext)) return 'Image'
  
  // Archive files
  if (['zip', 'tar', 'gz', 'rar', '7z'].includes(ext)) return 'Archive'
  
  return 'Unknown File Type'
} 