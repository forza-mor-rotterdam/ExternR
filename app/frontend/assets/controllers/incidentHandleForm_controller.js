import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['externalText', 'internalText', 'newTask', 'form']

  connect() {
    this.requiredLabelInternalText = 'Waarom kan de taak niet worden afgerond?'
    this.defaultLabelInternalText = 'Interne opmerking'
    this.defaultErrorMessage = 'Vul a.u.b. dit veld in.'
    const btn = this.element.querySelector('[type="radio"][value="niet_opgelost"]')
    if (btn.checked) {
      this.onResolutionFalse()
    } else {
      this.onResolutionTrue()
    }
  }

  onResolutionFalse() {
    if (this.hasInternalTextTarget) {
      this.internalTextTarget.querySelector('label').textContent = this.requiredLabelInternalText
      this.internalTextTarget.querySelector('textarea').classList.add('required')
      this.internalTextTarget.closest('.wrapper--flex-order').style.flexDirection = 'column-reverse'
    }
  }

  onResolutionTrue() {
    if (this.hasInternalTextTarget) {
      this.internalTextTarget.querySelector('label').textContent = this.defaultLabelInternalText
      this.internalTextTarget.querySelector('textarea').classList.remove('required')
      this.internalTextTarget.closest('.wrapper--flex-order').style.flexDirection = 'column'
    }
  }

  onChangeResolution(event) {
    if (event.target.value === 'niet_opgelost') {
      this.onResolutionFalse()
    } else {
      this.onResolutionTrue()
    }
  }

  checkValids() {
    const inputList = document.querySelectorAll('textarea')
    let count = 0
    for (const input of inputList) {
      let error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]
      let invalid = input.value.length == 0 && input.classList.contains('required')
      error.textContent = invalid ? this.defaultErrorMessage : ''
      input.closest('.form-row').classList[invalid ? 'add' : 'remove']('is-invalid')
      if (invalid) {
        count++
      }
    }
    return count === 0
  }

  onSubmit(event) {
    const allFieldsValid = this.checkValids()
    event.preventDefault()
    if (allFieldsValid) {
      this.formTarget.requestSubmit()
    }
  }
}
