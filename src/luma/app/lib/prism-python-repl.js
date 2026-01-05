/**
 * Extends Prism's Python language to tokenize REPL prompts (>>> and ...)
 * This allows CSS to make prompts non-selectable with user-select: none
 */

// Insert prompt token before other Python tokens
// This ensures >>> and ... at line starts are recognized as prompts, not operators/punctuation
Prism.languages.insertBefore("python", "comment", {
  prompt: {
    pattern: /^(?:>>>|\.\.\.)\s*/m,
    greedy: true,
  },
});
