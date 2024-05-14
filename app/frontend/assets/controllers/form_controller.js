import { Controller } from '@hotwired/stimulus'

let selectOptions = null

export default class extends Controller {
  static targets = ['searchSelect']

  initialize() {
    let self = this
    selectOptions = []
    if (self.hasSearchSelectTarget) {
      const options = self.searchSelectTarget.querySelectorAll('option')
      for (const option of options) {
        selectOptions.push({ value: option.value, label: option.textContent })
      }
    }
  }

  connect() {}

  searchFieldChangee(e) {
    let self = this
    if (!self.hasSearchSelectTarget) {
      return
    }
    self.searchSelectTarget.innerHTML = ''

    for (const optionData of selectOptions) {
      const re = new RegExp(e.target.value, 'gi')
      if (re.test(optionData.label)) {
        let option = document.createElement('option')
        // let newContent = selectOptions[i].label
        option.value = optionData.value
        option.textContent = optionData.label
        // option.innerHTML = newContent.replace(re, function(match) {
        //     return "<mark style='color:red;'>" + match + "</mark>";
        // })
        self.searchSelectTarget.appendChild(option)
      }
    }
  }
}
