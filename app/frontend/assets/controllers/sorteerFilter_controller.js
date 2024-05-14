import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['form', 'sorteerField']
  static values = {
    requestType: String,
  }

  connect() {
    if (this.hasRequestTypeValue && this.requestTypeValue == 'post') {
      let orderChangeEvent = new CustomEvent('orderChangeEvent', {
        bubbles: true,
        cancelable: false,
        detail: { order: this.sorteerFieldTarget.value },
      })
      this.element.dispatchEvent(orderChangeEvent)
    }
  }
  onChangeHandler() {
    this.formTarget.requestSubmit()
  }
}
