import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    taakId: String,
    url: String,
  }

  static targets = ['teller', 'vorige', 'volgende']

  initialize() {
    const taakIdList = sessionStorage.getItem('taakIdList').split(',')
    const taakId = Number(this.taakIdValue)
    const isCurrentTask = (id) => Number(id) === taakId
    const index = taakIdList.findIndex(isCurrentTask)
    const url = this.urlValue
    let previousId = 0
    let nextId = 0

    this.tellerTarget.innerHTML = `${index + 1} van ${taakIdList.length}`

    previousId = taakIdList[index - 1]
    nextId = taakIdList[index + 1]

    if (previousId) {
      this.vorigeTarget.setAttribute('href', `${url}${previousId}`)
      this.vorigeTarget.classList.remove('disabled')
    } else {
      this.vorigeTarget.classList.add('disabled')
    }
    if (nextId) {
      this.volgendeTarget.setAttribute('href', `${url}${nextId}`)
      this.volgendeTarget.classList.remove('disabled')
    } else {
      this.volgendeTarget.classList.add('disabled')
    }
  }
}
