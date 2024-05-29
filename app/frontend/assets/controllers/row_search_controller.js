// src/controllers/clipboard_controller.js
import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['row', 'searchable']

  connect() {
    this.searchableTargets.forEach((td) => {
      td.dataset.value = td.textContent
    })
  }
  search(e) {
    this.rowTargets.forEach((tr) => {
      tr.style.display = 'none'
    })
    this.searchableTargets.forEach((td) => {
      const re = new RegExp(e.target.value, 'gi')
      let newContent = td.dataset.value
      if (re.test(td.dataset.value)) {
        td.parentElement.style.display = 'table-row'
        newContent = newContent.replace(re, function (match) {
          return '<mark>' + match + '</mark>'
        })
      }
      td.innerHTML = newContent
    })
  }
}
