import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['form', 'zoekField']

  connect() {
    this.to = null
    this.csrf_token = this.element.querySelector('input[name="csrfmiddlewaretoken"]').value
  }
  updateTakenList() {
    let orderChangeEvent = new CustomEvent('searchChangeEvent', {
      bubbles: true,
      cancelable: false,
    })
    this.element.dispatchEvent(orderChangeEvent)
  }
  onChangeHandler() {
    clearTimeout(this.to)
    this.to = setTimeout(() => this.submit(this.zoekFieldTarget.value), 200)
  }

  onSubmit(event) {
    event.preventDefault()
  }

  async submit(q) {
    const zoekUrl = '/taak-zoeken/'
    try {
      const response = await fetch(`${zoekUrl}`, {
        method: 'post',
        headers: {
          'X-CSRFToken': this.csrf_token,
        },
        body: JSON.stringify({
          q: q,
        }),
      })
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`)
      }
      const data = await response.json()
      this.updateTakenList()
      return data.q
    } catch (error) {
      console.error('Error fetching address details:', error.message)
    }
  }
}
