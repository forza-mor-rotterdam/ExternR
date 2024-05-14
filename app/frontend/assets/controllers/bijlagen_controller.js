import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    //clear the filelist
    this.temp_files = {}
    this.temp_filesArr = []
    this.fileInput = this.element.querySelector("input[type='file']")
    this.multiple = this.fileInput.hasAttribute('multiple')
  }

  removeDuplicates(arr) {
    let unique = []
    arr.forEach((element) => {
      if (!unique.includes(element)) {
        unique.push(element)
      }
    })
    return unique
  }

  showFileInput() {
    const inputContainer = this.fileInput.parentElement
    inputContainer.classList.toggle('hidden')
  }

  removeFile(e) {
    const index = e.params.index
    const input = this.fileInput
    this.temp_filesArr = [...this.temp_files]
    this.temp_filesArr.splice(index, 1)

    /** Code from: https://stackoverflow.com/a/47172409/8145428 */
    const dT =
      new ClipboardEvent('').clipboardData || // Firefox < 62 workaround exploiting https://bugzilla.mozilla.org/show_bug.cgi?id=1422655
      new DataTransfer() // specs compliant (as of March 2018 only Chrome)

    for (let file of this.temp_filesArr) {
      dT.items.add(file)
    }
    this.temp_files = dT.files
    input.files = dT.files

    this.updateImageDisplay(false)
  }

  addFiles(newFiles) {
    if (this.temp_filesArr.length === 0) {
      this.temp_filesArr = [...newFiles]
    } else {
      this.temp_filesArr.push(...newFiles)
    }
    this.updateInputFiles()
  }

  updateInputFiles() {
    const input = this.fileInput
    const dT = new ClipboardEvent('').clipboardData || new DataTransfer()
    this.temp_filesArr.forEach((file) => {
      dT.items.add(file)
    })
    this.temp_files = dT.files
    input.files = dT.files
  }

  updateImageDisplay(adding = true) {
    const input = this.fileInput
    const preview = this.element.querySelector('.preview')
    const newFiles = input.files //contains only new file(s)

    if (!this.multiple) {
      this.temp_filesArr = []
    }
    if (adding) {
      this.addFiles(newFiles)
    }

    const fileTypes = [
      'image/apng',
      'image/bmp',
      'image/heic',
      'image/gif',
      'image/jpeg',
      'image/pjpeg',
      'image/png',
      'image/svg+xml',
      'image/tiff',
      'image/webp',
      'image/x-icon',
      'text/csv',
    ]

    function validFileType(file) {
      return fileTypes.includes(file.type)
    }

    function returnFileSize(number) {
      if (number < 1024) {
        return `${number} bytes`
      } else if (number >= 1024 && number < 1048576) {
        return `${(number / 1024).toFixed(1)} KB`
      } else if (number >= 1048576) {
        return `${(number / 1048576).toFixed(1)} MB`
      }
    }

    while (preview.firstChild) {
      preview.removeChild(preview.firstChild)
    }
    if (this.temp_files.length > 0) {
      const list = document.createElement('ul')
      list.classList.add('list-clean')
      preview.appendChild(list)

      for (const [index, file] of [...this.temp_files].entries()) {
        const listItem = document.createElement('li')
        const content = document.createElement('span')
        const remove = document.createElement('button')
        const span = document.createElement('span')
        span.classList.add('container__image')

        remove.setAttribute('type', 'button')
        remove.setAttribute('data-action', 'bijlagen#removeFile')
        remove.setAttribute('data-bijlagen-index-param', index)
        remove.classList.add('btn-close')

        if (validFileType(file)) {
          content.innerHTML = `${file.name} <small>${returnFileSize(file.size)}</small>`
          if (file.type === 'image/heic') {
            const placeholder = document.createElement('div')
            placeholder.classList.add('placeholder')
            span.textContent = 'Van dit bestandstype kan geen preview getoond worden.'
            placeholder.appendChild(span)
            listItem.appendChild(placeholder)
          } else if (file.type.includes('image/')) {
            const image = document.createElement('img')
            image.src = URL.createObjectURL(file)
            image.onload = () => {
              URL.revokeObjectURL(image.src)
            }
            span.appendChild(image)
            listItem.appendChild(span)
          }
          listItem.appendChild(content)
          listItem.appendChild(remove)
        } else {
          content.textContent = `Het bestand "${file.name}" is geen geldig bestandstype. Selecteer alleen bestanden van het type "jpg, jpeg of png"`
          listItem.appendChild(content)
        }

        list.appendChild(listItem)
      }
    }
  }
}
