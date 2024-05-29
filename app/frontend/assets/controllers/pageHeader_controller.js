import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {}

  resetFontSize() {
    document.body.classList.remove('fz-medium', 'fz-large', 'fz-xlarge')
  }

  setFontSize(e) {
    const size = e.params.size
    if (size) {
      this.resetFontSize()
      document.body.classList.add(size)
    }
  }
}
