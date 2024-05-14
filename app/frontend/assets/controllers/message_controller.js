import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    mercurePublicUrl: String,
  }
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
  initMessages() {
    let self = this
    if (self.hasMercurePublicUrlValue && self.isValidHttpUrl(self.mercurePublicUrlValue)) {
      // const url = new URL(self.mercurePublicUrlValue)
      // subscribe with a topic like below
      // url.searchParams.append('topic', [messages topic]);
      // self.eventSource = new EventSource(url);
      // self.eventSource.onmessage = e => self.onMessage(e)
      // self.eventSource.onerror = (e) => self.onMessageError(e)
    }
  }
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
