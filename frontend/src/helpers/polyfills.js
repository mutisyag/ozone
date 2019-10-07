const nodeListPrototypes = function() {
  if (window.NodeList) {
    if (!NodeList.prototype.forEach) {
      NodeList.prototype.forEach = Array.prototype.forEach
    }
  }
}

const nodePrototypes = function () {
  if (window.Node) {
    if (!Node.prototype.contains) {
      Node.prototype.contains = function (node) {
        if (!(0 in arguments)) {
          throw new TypeError('1 argument is required')
        }
        do {
          console.log(node)
          if (this === node) {
            return true
          }
        } while (node = node && node.parentNode)
        return false
      }
    }
  }
  
}

const loadPollyfills = function() {
  nodeListPrototypes()
  nodePrototypes()
}

export default loadPollyfills