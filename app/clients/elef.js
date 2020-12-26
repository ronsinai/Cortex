const Axios = require('axios');

module.exports = class Elef {
  constructor(url) {
    this.url = url;
  }

  async postDiagnosis(diagnosis) {
    return Axios.post(`${this.url}/diagnoses`, diagnosis);
  }
};
