const express = require("express")
const bodyParser = require("body-parser")
const Memcached = require("memcached")

const APP_HOST = '0.0.0.0'
const APP_PORT = 5650
const DB_HOST = 'localhost'
const DB_PORT = 5652

const app = express()
const memcached = new Memcached(`${DB_HOST}:${DB_PORT}`)

app.use(bodyParser())

async function getMessage () {
  return new Promise((resolve, reject) => {
    memcached.get('message', (err, result) => {
      if (err) return reject(err)
      if (typeof result === 'string') return resolve(result)
      resolve(0)
    })
  })
}

app.get('/api/message', async (_, res) => {
  const message = await getMessage()
  res.send({ message });
});

app.post('/api/message', async (req, res) => {
  // const sender = req.header('uniqys-sender')
  const { message } = req.body

  memcached.set(`message`, message, 0, (err) => {
    if (err) {
      res.status(400).send(err)
    }
    else {
      res.sendStatus(200)
    }
  })
})

app.listen(APP_PORT, APP_HOST)