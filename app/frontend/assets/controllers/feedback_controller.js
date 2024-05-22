import { Controller } from '@hotwired/stimulus'

const defaultErrorMessage = 'Vul a.u.b. dit veld in.'

export default class extends Controller {
  static targets = ['toelichting']

  initialize() {
    this.toelichtingTarget.querySelector('textarea').setAttribute('required', true)
  }

  connect() {}

  onChangeReden(e) {
    this.checkValids()
    if (e.target.value === '3') {
      const row = document.querySelector('textarea').closest('.form-row')
      const error = row.getElementsByClassName('invalid-text')[0]
      error.textContent = ''
      row.classList.remove('is-invalid')
      this.showField()
    } else {
      this.hideField(e)
    }
  }

  hideField(e) {
    this.toelichtingTarget.querySelector('textarea').value =
      e.target.parentNode.childNodes[1].nodeValue.trim()
    this.toelichtingTarget.classList.add('hidden')
  }

  showField() {
    const field = this.toelichtingTarget.querySelector('textarea')
    field.value = null
    this.toelichtingTarget.classList.remove('hidden')
    field.focus()
  }

  checkValids() {
    const inputList = document.querySelectorAll('[type="radio"], textarea')
    let count = 0
    for (const input of inputList) {
      const error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]

      if (input.validity.valid) {
        error.textContent = ''
        input.closest('.form-row').classList.remove('is-invalid')
      } else {
        error.textContent = defaultErrorMessage
        input.closest('.form-row').classList.add('is-invalid')
        count++
      }
    }
    return count === 0
  }

  onSubmit(event) {
    const allFieldsValid = this.checkValids()
    event.preventDefault()
    if (allFieldsValid) {
      this.element.submit()
    }
  }
}
