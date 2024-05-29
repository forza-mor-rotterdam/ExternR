import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {}
  initialize() {
    let self = this
    self.initMessages()
  }
  isValidHttpUrl(string) {
    let url

    try {
      url = new URL(string)
    } catch (_) {
      return false
    }

    return url.protocol === 'http:' || url.protocol === 'https:'
  }
  initMessages() {}
  // onMessage(e) {
  //   let data = JSON.parse(e.data)
  // }
  onMessageError(e) {
    let self = this
    console.log(e)
    console.log('An error occurred while attempting to connect.')
    self.eventSource.close()
  }
}
