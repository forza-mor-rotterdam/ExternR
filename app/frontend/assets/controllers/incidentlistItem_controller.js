import { Controller } from '@hotwired/stimulus'

let observer = null
export default class extends Controller {
  initialize() {
    // eslint-disable-next-line no-unused-vars
    observer = new IntersectionObserver((entries, { rootMargin = '20px', treshold = 0.0 }) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const container = entry.target.querySelectorAll('.background-image')[0]
          const imageSrc = container.getAttribute('data-src')
          if (imageSrc) {
            container.querySelector('img').src = imageSrc
            container.removeAttribute('data-src')
          }
        }
      })
    })
    observer.observe(this.element)
    this.element.addEventListener('click', () => {
      const pageNumber = this.element.dataset.page
      if (pageNumber !== '1') {
        sessionStorage.setItem('page_number', pageNumber)
      } else {
        sessionStorage.removeItem('page_number')
      }
    })
  }

  disconnect() {
    observer.disconnect(this.element)
  }
}
