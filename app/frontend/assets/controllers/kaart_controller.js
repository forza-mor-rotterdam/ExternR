import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

export default class MapController extends Controller {
  static outlets = ['main']
  static createMarkerIcons = () => ({
    blue: L.icon({
      iconUrl:
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAATESURBVHgBrVZNTGNVFL7vp9AfCB0mpAOSoRgdGUQcI8yiCYImGjXExBBYGbshcdGiKxHHhSVRdG+M0YWrccUC4qSz0EQT2RATiNHEBFKcjnYmg6BtLfa/7/qdx72vr50OU+qc5OTed9895zvn3HPOvYw1SZxzL/gt8Br4Bq8Szb8HB8F+9qAolUqdgcIIOMmbowj7vwQlg3XeNUu/5XK5wZN0Kw3AFBCDoN/pdH6HJb/8t3GTsWu7nEV3GbuZOl4b9TH2BPjKhMIGvDWqboCfA8dJ34nAApRjqmK+J0FTecY+2uDs0x/ZiRS6fGxAl7MKnkgkxvr7+5NCr0VqjRX4GYlE1Eql8r4d9KWr9wcloj0vY286by0N9vX1vWl6A6dqsOpkFSTTw11dXTG58M63zYHaKQzPP37eUp3c2tq6MDY29hfmltdqnRGqw+F4Vi7QOZ4WlIhkKB8EeUdGRoICS7kncFtb2+tyYWWDs1aIpKK7lqyiadpkQ2ARf2JdVdUB+fOXO6xlurZTnUPnaG9vr+Mu4OXlZWV4eFjr7u52YNN5+fPnP1nL9Hu6Bvh8qVTSCENiKjYD2sAueP+3FOj4sLVQS8WZ9ywHqU7P+v3+3Pj4eGl1dbVios/OziqoNaWzs1ODZQm5e6CLtUzUVCShPP/AoMbjcRWg5poJjA+lUChomUxGQ8f6VQpMX2At06gNGLpvsWpyKcz2wQ4ODszF/f19q4CmH1NYK0RS7z5TDXMsFltj1WO1gPnU1BTr6emhA+VLS0trCE2Gfk4gv0Pj7NQUuqzUHNP6+jo5owDDArfqGJlnAkej0X9g4Vdy/Qosf9LHmiYK8dJE9XtnZ+fzlZWVREdHh0HfcNLEMYEnJycNAWwg+yoLCwtX8/n8bfpHDf/6awoLjze4yhp4Snu94pKgsx0aGvoMo3F0dGTgOI16GTKAtp/BVUh1/Hg4HH4FiXbLfsnGU5y/8bXBA18Y3PPBMQ9/YvC3vzH4D/HaC5lkQ6HQNDrhsMvl6odOL8rJSZeQHZicoTruBJ9rb29/FOOl+fn5V7PZ7G1+SiIZkkXfvwQ9j4B9ON8OgXFX4DS0NTdq+SzmA7D0IsYxcGB7e/tL6DPuB4gekKG9gUDgBYA+DdmLIoLdYBdhSGClLtw6uB3shoDHMAw39FE3cwSDwYdmZmaeQud50ePxnEP4ekkIIb2TTCZje3t7Py0uLl7f3NxMAxQ2lHL4nQX/K8YCuMTE1VgtNlwUc3Nz1Fl0r9frKhaLLoTMTUZAERmjQ5nOqjcayXJd15VyuUxJw7GvjLGMfQSSdbvdWSICRXc0W6X9bOvPmsLhEMnmFCFyQmmbBCcwKQtQGgi4QsAClN4gOTwo8um0+R4hTyvM9hDQ2L3J9AJhNaDMIAKggeZSxrQCNkehlDiP7zyOIIfkzEEmjzIqoG5L6NGGHbSRx5JUVj1zh2DTY5y9jhrXoFyFXtNArBlYq8DIIi79IhKzdHh4SMaUpQPNAtuvS4qKhnKgm0vHm0yzGcbRkTiaAxehLKNWyUOaUxUY9a/LZsl8Dglw8tiJ65PO3CPZ5/N5qAzZcT44RJTU+ldlS0RKhCIz/Dg3XY7IVjMiYrSSrhmPWqFGcqcK6X9czfgLQYqNowAAAABJRU5ErkJggg==',
      iconSize: [26, 26],
      iconAnchor: [13, 13],
      popupAnchor: [0, -7],
    }),
    magenta: L.icon({
      iconUrl:
        'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMy43NzgzIDYuMjI0MTJDMTkuNTAwMyAxLjk0NjEzIDEyLjQ5OTkgMS45NDYxMyA4LjIyMTkzIDYuMjI0MTJDMy45NDM5MyAxMC41MDIxIDMuOTQzOTMgMTcuNTAyNSA4LjIyMTkzIDIxLjc4MDVMMTYuMDAwMSAyOS41NTg2TDIzLjc3ODMgMjEuNzgwNUMyOC4wNTYzIDE3LjUwMjUgMjguMDU2MyAxMC41MDIxIDIzLjc3ODMgNi4yMjQxMlpNMTYuMDAwMSAxOC4wMDIzQzE4LjIwOTIgMTguMDAyMyAyMC4wMDAxIDE2LjIxMTQgMjAuMDAwMSAxNC4wMDIzQzIwLjAwMDEgMTEuNzkzMiAxOC4yMDkyIDEwLjAwMjMgMTYuMDAwMSAxMC4wMDIzQzEzLjc5MSAxMC4wMDIzIDEyLjAwMDEgMTEuNzkzMiAxMi4wMDAxIDE0LjAwMjNDMTIuMDAwMSAxNi4yMTE0IDEzLjc5MSAxOC4wMDIzIDE2LjAwMDEgMTguMDAyM1oiIGZpbGw9IiNDOTM2NzUiLz4KPC9zdmc+Cg==',
      iconSize: [32, 32],
      iconAnchor: [16, 16],
      popupAnchor: [0, -8],
    }),
  })
  static markerIcons = MapController.createMarkerIcons()

  markerList = []
  markerMe = null
  map = null
  markers = null
  buurten = null

  initialize = () => {
    this.map = L.map('incidentMap', this.mainOutlet.getKaartStatus())

    if (this.element) {
      this.drawMap()
      this.setupEventListeners()
    }
  }

  setupEventListeners = () => {
    this.map.on('moveend zoomend', () => {
      this.mainOutlet.setKaartStatus({
        zoom: this.map.getZoom(),
        center: this.map.getCenter(),
      })
    })

    this.map.on('popupopen popupclose', ({ popup }) => {
      if (popup instanceof L.Popup) {
        const marker = popup._source
        const eventName = popup.isOpen() ? 'markerSelectedEvent' : 'markerDeselectedEvent'
        const event = new CustomEvent(eventName, {
          bubbles: true,
          cancelable: false,
          detail: { taakId: marker.options.taakId },
        })
        this.element.dispatchEvent(event)
      }
    })
  }

  drawMap = () => {
    const url =
      'https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}'

    const config = {
      crs: 'EPSG:3857',
      format: 'png',
      name: 'standaard',
      layerName: 'standaard',
      type: 'wmts',
      minZoom: 10,
      maxZoom: 19,
      tileSize: 256,
      attribution: '',
      gestureHandling: true,
    }

    L.tileLayer(url, config).addTo(this.map)

    this.setupResizeObserver()
    this.createMarkersLayer()

    this.buurten = L.tileLayer.wms(
      'https://service.pdok.nl/cbs/wijkenbuurten/2022/wms/v1_0?request=GetCapabilities&service=WMS',
      {
        layers: 'buurten',
        format: 'image/png',
        transparent: true,
        minZoom: 10,
        maxZoom: 19,
        srsName: 'EPSG:4326',
        bbox: '51.9247770, 4.4780970, 51.9247774, 4.4780974',
      }
    )
  }

  setupResizeObserver = () => {
    const resizeObserver = new ResizeObserver(() => {
      this.map.invalidateSize()
      this.element.dispatchEvent(
        new CustomEvent('markerDeselectedEvent', { bubbles: true, cancelable: false })
      )
      this.map.closePopup()
    })

    resizeObserver.observe(document.getElementById('incidentMap'))
  }

  createMarkersLayer = () => {
    this.markers = new L.featureGroup()
    this.map.addLayer(this.markers)
  }

  selectTaakMarker(taakId) {
    const obj = this.markerList.find((obj) => obj.options.taakId == taakId)
    obj.openPopup()
  }

  kaartModusChangeHandler = (_kaartModus) => {
    if (!this.markerMe) {
      return
    }
    this.mainOutlet.setKaartModus(_kaartModus)
    switch (_kaartModus) {
      case 'volgen':
        this.map.flyTo(this.markerMe.getLatLng(), this.mainOutlet.getKaartStatus().zoom)
        break

      case 'toon_alles':
        this.map.fitBounds(this.markers.getBounds())
        break
    }
  }

  onTwoFingerDrag(event) {
    if (event.type === 'touchstart' && event.touches.length === 1) {
      event.currentTarget.classList.add('swiping')
    } else {
      event.currentTarget.classList.remove('swiping')
    }
  }

  positionChangeEvent = (position) => {
    if (!this.markerMe) {
      this.markerMe = new L.Marker([position.coords.latitude, position.coords.longitude], {
        icon: MapController.markerIcons.blue,
      })
      this.markers.addLayer(this.markerMe)
    } else {
      this.markerMe.setLatLng([position.coords.latitude, position.coords.longitude])
    }
    if (this.mainOutlet.getKaartModus() === 'volgen') {
      this.map.setView(this.markerMe.getLatLng(), this.mainOutlet.getKaartStatus().zoom)
    }
  }

  toggleBuurten = () => {
    const checkbox = this.element.querySelector('#buurten-checkbox')
    const button = this.element.querySelector('#buurten-button')
    const isChecked = (checkbox.checked = !checkbox.checked)

    if (isChecked) {
      this.buurten.addTo(this.map)
    } else {
      this.map.removeLayer(this.buurten)
    }

    button.classList.toggle('active', isChecked)
    checkbox.classList.toggle('active', isChecked)
  }

  clearMarkers = () => {
    this.markerList = []
    this.markers.clearLayers()
    if (this.markerMe) {
      this.markers.addLayer(this.markerMe)
    }
  }

  plotMarkers = (coordinatenlijst) => {
    if (coordinatenlijst) {
      for (const coord of coordinatenlijst) {
        const lat = coord.geometrie.coordinates ? coord.geometrie.coordinates[1] : 51.9247772
        const long = coord.geometrie.coordinates ? coord.geometrie.coordinates[0] : 4.4780972
        const adres = coord.adres
        const afbeelding = coord.afbeeldingUrl
        const titel = coord.titel
        const taakId = coord.taakId

        const markerLocation = new L.LatLng(lat, long)

        const marker = new L.Marker(markerLocation, {
          icon: MapController.markerIcons.magenta,
          taakId: taakId,
        })

        const paragraphDistance = `<p>Afstand: <span data-incidentlist-target="taakAfstand" data-latitude="${lat}" data-longitude="${long}"></span> meter</p>`

        const popupContent = afbeelding
          ? `<div class="container__image"><img src=${afbeelding}></div><div class="container__content"><h5 class="no-margin">${adres}</h5><p>${titel}</p>${paragraphDistance}</div>`
          : `<div></div><div class="container__content"><h5 class="no-margin">${adres}</h5><p>${titel}</p>${paragraphDistance}</div>`

        marker.bindPopup(popupContent, { maxWidth: 460 })

        this.markers.addLayer(marker)
        this.markerList.push(marker)
      }
    }
  }
}
