document.body.classList.remove('no-js')

const questions = [
  {
    question: `Da's als kakken zonder douwen`,
    choices: [
      'Iets wat makkelijk is',
      'Praten zonder te luisteren',
      'Ander woord voor "buikgriep"',
    ],
    correct: 0,
  },
  {
    question: 'Bakkie Pleur',
    choices: ['Iemand die van zijn bakfiets is gevallen', 'Slecht weer', 'Een kop koffie'],
    correct: 2,
  },
  {
    question: 'Een dooie met een dag verlof',
    choices: ['Iemand die heel saai is', 'Iemand op zijn sterfbed', 'Iemand die heel lui is'],
    correct: 0,
  },
  {
    question: 'Je ken een hoop stront paars verve, maar ’t blijf een hoop stront',
    choices: [
      'Al draagt een aap een gouden ring, hij is en blijft een lelijk ding',
      'Een heel traag proces binnen de overheid',
      'Opruimen, maar het blijft toch een rotzooi',
    ],
    correct: 0,
  },
  {
    question: 'Boterklokkie',
    choices: [
      'Klokvormige beker waar vroeger boter in zat',
      'Een duur horloge',
      'Iemand die precies om 5 uur uitklokt',
    ],
    correct: 1,
  },
  {
    question: 'Hebbie in je nest gezeken?',
    choices: [
      'Iemand die vreemd is gegaan met een bekende',
      'Iemand wie zijn haar heel slecht zit',
      'Iemand die vroeg is opgestaan',
    ],
    correct: 2,
  },
  {
    question: 'De reuzel loop m’n reet uit',
    choices: [
      'Iemand verkoopt onzin',
      'Last hebben van diarree',
      'Wat is het verschrikkelijk warm',
    ],
    correct: 2,
  },
  {
    question: 'Hij heb een snee in z’n neus',
    choices: ['Hij is dronken', 'Hij is onhandig', 'Hij is een klikspaan'],
    correct: 0,
  },
  {
    question: 'As tie doodgeschoten wordt is tie nog te beroerd om te vallen',
    choices: ['Iemand die extreem lui is', 'Iemand die kerngezond is', 'Iemand die arrogant is'],
    correct: 0,
  },
  {
    question: 'Hij staat zelf tegen de pui te pisse om een hond uit te sparen',
    choices: ['Hij is extreem lui', 'Hij is extreem gierig', 'Hij is extreem ijverig'],
    correct: 1,
  },
  {
    question: 'Wat een bek heb die vent. En daar mottie nog mee vreten ook',
    choices: ['Hij vloekt heel veel', 'Wat is hij lelijk', 'Hij heeft scheve tanden'],
    correct: 1,
  },
  {
    question: 'Opoe Herfst',
    choices: ['De dood', 'Het jaargetijde', 'Een bemoeial'],
    correct: 2,
  },
  {
    question: 'Hard voor weinig, maar nooit chagrijnig',
    choices: [
      'Iemand die altijd positief is',
      'Ik werk hard en verdien heel weinig, maar heb het toch naar mijn zin',
      'Een marktkoopman',
    ],
    correct: 1,
  },
  {
    question: 'Zeike en scheite',
    choices: ['Iemand die zeurt', 'Iemand die de politiek in gaat', 'Twee dingen tegelijk doen'],
    correct: 2,
  },
  {
    question: 'Hij heb ’m een end uit z’n broek hangen',
    choices: [
      'Iemand die dronken is',
      'Iemand ie veel geld uitgeeft',
      'Iemand die zijn partner slaat',
    ],
    correct: 1,
  },
]
let rightAnswerGiven = false
const index = Math.floor(questions.length * Math.random())
console.log('questions', index)
console.log('questions[index].choices', questions[index].choices)
document.getElementById('errorpageQuestion').textContent = questions[index].question
for (let i = 0; i < questions[index].choices.length; i++) {
  let btn = document.createElement('button')
  btn.classList.add('btn')
  btn.textContent = questions[index].choices[i]
  btn.addEventListener('click', function () {
    if (!rightAnswerGiven) {
      if (i === questions[index].correct) {
        rightAnswerGiven = true
        this.classList.add('right-answer')
        this.parentNode.classList.add('right-answer-given')
        confettiLoop()
      } else {
        this.classList.add('wrong-answer')
      }
      this.blur()
    }
  })
  document.getElementById('errorpageContainerAnswers').appendChild(btn)
}

// global variables
const confetti = document.getElementById('confetti')
const confettiCtx = confetti.getContext('2d')
let container,
  confettiElements = [],
  clickPosition

// helper
const rand = (min, max) => Math.random() * (max - min) + min

// params to play with
const confettiParams = {
  // number of confetti per "explosion"
  number: 70,
  // min and max size for each rectangle
  size: { x: [5, 20], y: [10, 18] },
  // power of explosion
  initSpeed: 25,
  // defines how fast particles go down after blast-off
  gravity: 0.65,
  // how wide is explosion
  drag: 0.08,
  // how slow particles are falling
  terminalVelocity: 6,
  // how fast particles are rotating around themselves
  flipSpeed: 0.017,
}

const colors = [
  { front: '#00811f', back: '#006e32' },
  { front: '#c93675', back: '#a12b5e' },
  { front: '#00811f', back: '#006e32' },
  { front: '#c93675', back: '#a12b5e' },
  { front: '#00811f', back: '#006e32' },
  { front: '#c93675', back: '#a12b5e' },
  { front: '#00811f', back: '#006e32' },
  { front: '#c93675', back: '#a12b5e' },
  { front: '#ffc107', back: '#fd7e14' },
  { front: '#20c997', back: '#0dcaf0' },
]

setupCanvas()
updateConfetti()

window.addEventListener('resize', () => {
  setupCanvas()
})

// Confetti constructor
function Conf() {
  this.randomModifier = rand(-1, 1)
  this.colorPair = colors[Math.floor(rand(0, colors.length))]
  this.dimensions = {
    x: rand(confettiParams.size.x[0], confettiParams.size.x[1]),
    y: rand(confettiParams.size.y[0], confettiParams.size.y[1]),
  }
  this.position = {
    x: clickPosition[0],
    y: clickPosition[1],
  }
  this.rotation = rand(0, 2 * Math.PI)
  this.scale = { x: 1, y: 1 }
  this.velocity = {
    x: rand(-confettiParams.initSpeed, confettiParams.initSpeed) * 0.4,
    y: rand(-confettiParams.initSpeed, confettiParams.initSpeed),
  }
  this.flipSpeed = rand(0.2, 1.5) * confettiParams.flipSpeed

  if (this.position.y <= container.h) {
    this.velocity.y = -Math.abs(this.velocity.y)
  }

  this.terminalVelocity = rand(1, 1.5) * confettiParams.terminalVelocity

  this.update = function () {
    this.velocity.x *= 0.98
    this.position.x += this.velocity.x

    this.velocity.y += this.randomModifier * confettiParams.drag
    this.velocity.y += confettiParams.gravity
    this.velocity.y = Math.min(this.velocity.y, this.terminalVelocity)
    this.position.y += this.velocity.y

    this.scale.y = Math.cos((this.position.y + this.randomModifier) * this.flipSpeed)
    this.color = this.scale.y > 0 ? this.colorPair.front : this.colorPair.back
  }
}

function updateConfetti() {
  confettiCtx.clearRect(0, 0, container.w, container.h)

  confettiElements.forEach((c) => {
    c.update()
    confettiCtx.translate(c.position.x, c.position.y)
    confettiCtx.rotate(c.rotation)
    const width = c.dimensions.x * c.scale.x
    const height = c.dimensions.y * c.scale.y
    confettiCtx.fillStyle = c.color
    confettiCtx.fillRect(-0.5 * width, -0.5 * height, width, height)
    confettiCtx.setTransform(1, 0, 0, 1, 0, 0)
  })

  confettiElements.forEach((c, idx) => {
    if (
      c.position.y > container.h ||
      c.position.x < -0.5 * container.x ||
      c.position.x > 1.5 * container.x
    ) {
      confettiElements.splice(idx, 1)
    }
  })
  window.requestAnimationFrame(updateConfetti)
}

function setupCanvas() {
  container = {
    w: confetti.clientWidth,
    h: confetti.clientHeight,
  }
  confetti.width = container.w
  confetti.height = container.h
}

function addConfetti(e) {
  const canvasBox = confetti.getBoundingClientRect()
  if (e) {
    clickPosition = [e.clientX - canvasBox.left, e.clientY - canvasBox.top]
  } else {
    clickPosition = [canvasBox.width * Math.random(), canvasBox.height * Math.random()]
  }
  for (let i = 0; i < confettiParams.number; i++) {
    confettiElements.push(new Conf())
  }
}

function confettiLoop() {
  addConfetti()
  const interval = setInterval(addConfetti, 700 + Math.random() * 700)
  window.setTimeout(() => {
    clearInterval(interval)
  }, 8000)
}

let whatsapp_url = 'https://web.whatsapp.com/'
const waLink = document.getElementById('errorPageWaLink')
const errorMessage = waLink.getAttribute('data-errorValue')
console.log('errormessage', errorMessage)
if (isMobile()) {
  whatsapp_url = 'whatsapp://'
}

// timestamp
const now = new Date()
const dateTime = now.toLocaleString()

whatsapp_url += `send?text=${errorMessage} - tijdstip (gebruiker): ${dateTime}`

waLink.href = whatsapp_url

function isMobile() {
  const regex = /Mobi|Android|iPhone|BlackBerry|IEMobile|Opera Mini/i
  return regex.test(navigator.userAgent)
}
