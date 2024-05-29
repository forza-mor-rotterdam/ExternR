import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['form']
  static values = {
    requestType: String,
  }

  connect() {
    this.dispatchKaartModusChangeEvent()
  }

  dispatchKaartModusChangeEvent() {
    const field = this.formTarget.querySelector("[name='kaart_modus']:checked")
    const kaartModusChangeEvent = new CustomEvent('kaartModusChangeEvent', {
      bubbles: true,
      cancelable: false,
      detail: {
        kaartModus: field.value,
        requestType: this.requestTypeValue,
      },
    })
    this.element.dispatchEvent(kaartModusChangeEvent)
    field.parentNode.classList.add('active')
  }

  kaartModusOptionClickHandler(event) {
    if (event.target.matches("[name='kaart_modus']")) {
      this.formTarget.requestSubmit()
    }
  }
}
