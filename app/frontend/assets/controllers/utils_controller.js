import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  // static params = ["url"]

  initialize() {}

  connect() {}

  goToUrl(e) {
    window.location.href = e.params.url
  }
}
