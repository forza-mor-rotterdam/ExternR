import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  initialize() {
    setTimeout(() => this.element.classList.add('show'), 10)
    setTimeout(() => this.element.classList.remove('show'), 7000)
    setTimeout(() => this.element.remove(), 8000)
  }
}
