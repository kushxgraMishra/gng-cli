# Shell integration: change the current zsh directory with `gng open` or `gng cd`.
# Other GNG commands continue to run through the installed Python CLI.
gng() {
  if [[ "${1-}" == "open" || "${1-}" == "cd" ]]; then
    if [[ "${2-}" == "--help" || "${2-}" == "-h" ]]; then
      command gng "$@"
      return $?
    fi

    shift
    if (( $# > 1 )); then
      print -u2 -- "usage: gng open [folder]"
      return 2
    fi

    local target="${1:-.}"
    if [[ ! -d "$target" ]]; then
      print -u2 -- "gng: no such folder: $target"
      return 1
    fi

    builtin cd -- "$target"
    return $?
  fi

  command gng "$@"
}
