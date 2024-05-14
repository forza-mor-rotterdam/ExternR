import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

export default class extends Controller {
  static outlets = ['taken']

  currentPosition = { coords: { latitude: 51.9247772, longitude: 4.4780972 } }
  incidentlist = null
  detail = null
  kaartModus = null
  kaartStatus = null

  initialize() {
    const status = {
      zoom: 16,
      center: [this.currentPosition.coords.latitude, this.currentPosition.coords.longitude],
    }
    this.kaartModus = 'volgen'
    this.kaartStatus = {
      volgen: status,
      toon_alles: status,
    }
    if (!sessionStorage.getItem('kaartStatus')) {
      sessionStorage.setItem('kaartStatus', JSON.stringify(this.kaartStatus))
    }

    navigator.geolocation.getCurrentPosition(
      this.getCurrentPositionSuccess,
      this.positionWatchError
    )

    window.addEventListener(
      'childControllerConnectedEvent',
      this.childControllerConnectedEventHandler
    )
  }

  childControllerConnectedEventHandler = (e) => {
    if (e.detail.controller.identifier === 'incidentlist') {
      this.incidentlist = e.detail.controller
      this.incidentlist.positionWatchSuccess(this.currentPosition)
    }
    if (e.detail.controller.identifier === 'detail') {
      this.detail = e.detail.controller
      this.detail.positionWatchSuccess(this.currentPosition)
    }
  }

  getCurrentPositionSuccess = (position) => {
    this.positionWatchSuccess(position)
  }

  positionWatchSuccess = (position) => {
    const myLocation = new L.LatLng(
      this.currentPosition.coords.latitude,
      this.currentPosition.coords.longitude
    )
    const distance = myLocation.distanceTo([position.coords.latitude, position.coords.longitude])
    if (distance > 5) {
      this.currentPosition = position
      if (this.incidentlist) {
        this.incidentlist.positionWatchSuccess(position)
      }
      if (this.detail) {
        this.detail.positionWatchSuccess(position)
      }
    }
  }

  positionWatchError = (error) => {
    console.log('positionWatchError controller id:', this.identifier)
    console.log('handleNoCurrentLocation, error: ', error)
    switch (error.code) {
      case error.PERMISSION_DENIED:
        console.log('User denied the request for Geolocation.')
        break
      case error.POSITION_UNAVAILABLE:
        console.log('Location information is unavailable.')
        break
      case error.TIMEOUT:
        console.log('The request to get user location timed out.')
        break
      case error.UNKNOWN_ERROR:
        console.log('An unknown error occurred.')
        break
    }
    this.getCurrentPositionSuccess(this.currentPosition)
  }

  showFilters() {
    document.body.classList.add('show-filters')
  }

  hideFilters() {
    document.body.classList.remove('show-filters')
  }

  setKaartModus(_kaartModus) {
    this.kaartModus = _kaartModus
  }

  getCurrentPosition() {
    return this.currentPosition
  }

  getKaartModus() {
    return this.kaartModus
  }

  setKaartStatus(_kaartStatus) {
    this.kaartStatus[this.kaartModus] = _kaartStatus
    const sessionState = JSON.parse(sessionStorage.getItem('kaartStatus')) || {}
    sessionState[this.kaartModus] = _kaartStatus
    sessionStorage.setItem('kaartStatus', JSON.stringify(sessionState))
  }

  getKaartStatus() {
    const sessionState = JSON.parse(sessionStorage.getItem('kaartStatus')) || {}
    return sessionState[this.kaartModus]
  }
}
