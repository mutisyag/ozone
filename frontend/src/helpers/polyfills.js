const nodeListPrototypes = () => {
  if (window.NodeList) {
    if (!NodeList.prototype.forEach) {
      NodeList.prototype.forEach = Array.prototype.forEach
    }
  }
}

const nodePrototypes = (...args) => {
  if (window.Node) {
    if (!Node.prototype.contains) {
      Node.prototype.contains = (node) => {
        if (args.length < 1) {
          throw new TypeError('1 argument is required')
        }
        do {
          if (this === node) {
            return true
          }
          node = node && node.parentNode
        } while (node)
        return false
      }
    }
  }
}

const loadPollyfills = () => {
  nodeListPrototypes()
  nodePrototypes()
}

export default loadPollyfills
