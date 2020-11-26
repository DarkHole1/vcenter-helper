const axios = require('axios');
const querystring = require('querystring');
const express = require('express');
const app = express();

const auth = {
  server: process.env.VCENTER_SERVER,
  user: process.env.VCENTER_USER,
  pass: process.env.VCENTER_PASSWORD
};

function* range(str) {
  let nums = str.split(',');
  for(let num of nums) {
    parsed = num.split('-').map(e => parseInt(e));
    if(parsed.length === 2) {
      if(!isFinite(parsed[0]) || !isFinite(parsed[1])) continue;
      for(let i = parsed[0]; i <= parsed[1]; i++) {
        yield i;
      }
      continue;
    }
    if(parsed.length === 1) {
      if(!isFinite(parsed[0])) continue;
      yield parsed[0];
    }
  }
}

function formatName(str, num) {
  return str.replace(/{num:(\d+)}/g, function(match, p1) {
    return num.toString().padStart(p1, '0');
  });
}

app.get('/action/massclone', async (req, res) => {
  let commonParams = {
    source: req.query.vm,
    folder: req.query.folder,
    datastore: req.query.datastore,
    host: req.query.host,
    pool: req.query.pool
  };
  for(let i of range(req.query.nums)) {
    let resp = await axios.get('http://localhost:5000/api/machine:clone', {
      params: Object.assign(
        {}, auth, commonParams,
        { name: formatName(req.query.name, i)}
      )
    });
    resp = resp.data;
    console.log(resp);
  }
  res.json({ success: true });
});
app.use(express.static(__dirname + '/frontend'));

app.listen(3000);
