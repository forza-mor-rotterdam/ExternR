import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = [
    'turboFormHandler',
    'incidentDate',
    'buttonNietOpgelost',
    'buttonOpgelost',
    'swipeContainer',
  ]
  static values = {
    date: String,
    days: String,
  }

  initialize() {
    let self = this
    self.element[self.identifier] = self
    self.lock = false
    if (self.element.classList.contains('list-item')) {
      self.initialTouchPos = null
      self.bindStart = self.handleGestureStart.bind(self)
      self.bindMove = self.handleGestureMove.bind(self)
      self.bindEnd = self.handleGestureEnd.bind(self)
      self.addInitialListeners()
      self.isMoving = false

      if (!!self.dateValue && !!self.daysValue) {
        self.incidentDateTarget.textContent = self.getNumberOfDays(
          self.dateValue,
          parseInt(self.daysValue)
        )
      }
    }
  }

  getNumberOfDays(date, days) {
    const date_incident = new Date(date)
    const dateTypes = ['Vandaag', 'Gisteren', 'Eergisteren', 'dagen']
    if (days < 3) {
      const minutes =
        date_incident.getMinutes() < 10
          ? `0${date_incident.getMinutes()}`
          : date_incident.getMinutes()
      const time = `${date_incident.getHours()}:${minutes}`
      return `${dateTypes[1]}, ${time}`
    } else {
      return `${days} werkdagen`
    }
  }

  addInitialListeners() {
    let self = this
    // Safari on iOS does not apply the active state by default
    if (/iP(hone|ad)/.test(window.navigator.userAgent)) {
      document.body.addEventListener('touchstart', function () {}, false)
    }
    if (window.PointerEvent) {
      // Add Pointer Event Listener
      self.swipeContainerTarget.addEventListener('pointerdown', self.bindStart, false)
    } else {
      // Add Touch Listener
      self.swipeContainerTarget.addEventListener('touchstart', self.bindStart, false)
      // Add Mouse Listener
      self.swipeContainerTarget.addEventListener('mousedown', self.bindStart, false)
    }
  }

  addAllListeners() {
    let self = this
    // Check if pointer events are supported.
    if (window.PointerEvent) {
      // Add Pointer Event Listener
      self.swipeContainerTarget.addEventListener('pointerdown', self.bindStart, false)
      self.swipeContainerTarget.addEventListener('pointermove', self.bindMove, false)
      self.swipeContainerTarget.addEventListener('pointerup', self.bindEnd, false)
      self.swipeContainerTarget.addEventListener('pointercancel', self.bindEnd, false)
    } else {
      // Add Touch Listener
      self.swipeContainerTarget.addEventListener('touchstart', self.bindStart, false)
      self.swipeContainerTarget.addEventListener('touchmove', self.bindMove, false)
      self.swipeContainerTarget.addEventListener('touchend', self.bindEnd, false)
      self.swipeContainerTarget.addEventListener('touchcancel', self.bindEnd, false)
      // Add Mouse Listener
      self.swipeContainerTarget.addEventListener('mousedown', self.bindStart, false)
    }
  }

  removeAllListeners() {
    let self = this
    // Check if pointer events are supported.
    if (window.PointerEvent) {
      // Add Pointer Event Listener
      self.swipeContainerTarget.removeEventListener('pointerdown', self.bindStart, false)
      self.swipeContainerTarget.removeEventListener('pointermove', self.bindMove, false)
      self.swipeContainerTarget.removeEventListener('pointerup', self.bindEnd, false)
      self.swipeContainerTarget.removeEventListener('pointercancel', self.bindEnd, false)
    } else {
      // Add Touch Listener
      self.swipeContainerTarget.removeEventListener('touchstart', self.bindStart, false)
      self.swipeContainerTarget.removeEventListener('touchmove', self.bindMove, false)
      self.swipeContainerTarget.removeEventListener('touchend', self.bindEnd, false)
      self.swipeContainerTarget.removeEventListener('touchcancel', self.bindEnd, false)
      // Add Mouse Listener
      self.swipeContainerTarget.removeEventListener('mousedown', self.bindStart, false)
    }
  }

  // Handle the start of gestures
  handleGestureStart(evt) {
    let self = this
    this.element.classList.add('selected')
    evt.preventDefault()
    self.isMoving = false
    if (evt.touches && evt.touches.length > 1) {
      return
    }

    self.addAllListeners()
    self.initialTouchPos = self.getGesturePointFromEvent(evt)
  }

  // Handle end gestures
  handleGestureEnd(evt) {
    let self = this
    evt.preventDefault()
    if (evt.touches && evt.touches.length > 0) {
      return
    }

    // self.removeAllListeners()
    self.updateSwipeRestPosition(evt)

    self.initialTouchPos = null
    if (self.isMoving !== true) {
      self.isMoving = false
    }
  }

  handleGestureMove(evt) {
    let self = this
    evt.preventDefault()
    self.isMoving = true
    if (!self.initialTouchPos) {
      return
    }

    self.lastTouchPos = self.getGesturePointFromEvent(evt)
    self.onAnimFrame()
  }

  getGesturePointFromEvent = function (evt) {
    let point = {}

    if (evt.targetTouches) {
      // Prefer Touch Events
      point.x = evt.targetTouches[0].clientX
      point.y = evt.targetTouches[0].clientY
    } else {
      // Either Mouse event or Pointer Event
      point.x = evt.clientX
      point.y = evt.clientY
    }

    return point
  }

  onAnimFrame() {
    let self = this
    let differenceInX = self.initialTouchPos.x - self.lastTouchPos.x
    let newLeft = 0 - differenceInX + 'px'
    let leftStyle = newLeft
    if (self.lock) {
      return
    }
    if (differenceInX > -100 && differenceInX < 100) {
      self.element.style.left = leftStyle
    } else if (differenceInX <= -100) {
      self.element.style.left = '100%'
      self.lock = true
      setTimeout(function () {
        self.buttonNietOpgelostTarget.click()
        self.resetIncidentSwipe()
      }, 500)
    } else {
      self.lock = true
      self.element.style.left = '-100%'
      setTimeout(function () {
        self.buttonOpgelostTarget.click()
        self.resetIncidentSwipe()
      }, 500)
    }
  }

  resetIncidentSwipe() {
    let self = this
    self.removeAllListeners()
    self.addInitialListeners()
    setTimeout(function () {
      self.element.style.left = '0'
      self.lock = false
    }, 1000)
  }

  updateSwipeRestPosition(evt) {
    let self = this
    if (self.lastTouchPos) {
      let differenceInX = self.initialTouchPos.x - self.lastTouchPos.x
      if (differenceInX > -100 && differenceInX < 100) {
        self.element.style.left = '0'
      }
      self.initialTouchPos = self.getGesturePointFromEvent(evt)
    }
  }
}
