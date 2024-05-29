import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['modal', 'modalBackdrop']
  static values = {
    session_expiry_timestamp: String,
    session_expiry_max_timestamp: String,
    session_check_interval: String,
  }
  initialize() {}
  connect() {
    let self = this
    self.sessionTimer()
  }

  openModal() {
    let self = this
    self.modalTarget.classList.add('show')
    self.modalBackdropTarget.classList.add('show')
    document.body.classList.add('show-modal')
  }

  closeModal() {
    let self = this
    window.location.reload(true)
    self.modalTarget.classList.remove('show')
    self.modalBackdropTarget.classList.remove('show')
    document.body.classList.remove('show-modal')
  }

  sessionTimer() {
    let self = this
    const sessionExpiryTimestamp = parseInt(self.sessionExpiryTimestampValue) * 1000
    const sessionExpiryMaxTimestamp = parseInt(self.sessionExpiryMaxTimestampValue) * 1000
    const sessionCheckInterval = parseInt(self.sessionCheckIntervalValue)
    let timer = setInterval(function () {
      const currentDate = new Date()
      const timeIsUp = sessionExpiryTimestamp <= parseInt(parseInt(currentDate.getTime()))
      const timeIsUpMax = sessionExpiryMaxTimestamp <= parseInt(parseInt(currentDate.getTime()))
      if (timeIsUp || timeIsUpMax) {
        clearInterval(timer)
        self.openModal()
      }
    }, 1000 * sessionCheckInterval)
  }
}
