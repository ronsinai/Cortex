const Chai = require('chai');
const chaiAsPromised = require('chai-as-promised');
const Nconf = require('nconf');
const Sinon = require('sinon');
const SinonChai = require('sinon-chai');
const { ValidationError } = require('joi');

Chai.use(chaiAsPromised);
Chai.use(SinonChai);
const { expect } = Chai;

const exampleImaging = require('../data/imaging');
const { getMessage } = require('../utils/mq');

describe('Consumer', () => {
  before(() => {
    this.exampleImaging = exampleImaging;
    this.badImaging = { _id: 'partial' };

    const { _id, type } = exampleImaging;
    this.exampleDiagnosis = { imagingId: _id, imagingType: type, diagnosis: Nconf.get('AMQP_IN_QUEUE') };
    this.badDiagnosis = { imagingId: 'partial' };

    this.mq = global.consumerInstance.mq;

    this.algorithm = this.mq.algorithm;
    this.channel = this.mq.channel;
  });

  beforeEach(() => {
    this.algorithmSpy = Sinon.spy(this.algorithm, 'run');

    this.publishStub = Sinon.stub(this.channel, 'publish');
    this.ackStub = Sinon.stub(this.channel, 'ack');
    this.rejectStub = Sinon.stub(this.channel, 'reject');
  });

  afterEach(() => {
    this.algorithmSpy.restore();

    this.publishStub.restore();
    this.ackStub.restore();
    this.rejectStub.restore();
  });

  describe('Algorithm', () => {
    describe('#run', () => {
      it('should compute diagnosis', () => {
        const diagnosis = this.algorithm.run(this.exampleImaging);
        expect(diagnosis).to.eql(this.exampleDiagnosis);
      });

      it('should fail when given partial imaging', () => {
        expect(this.algorithm.run.bind(this, this.badImaging)).to.throw(ValidationError, '"type" is required');
      });
    });
  });

  describe('Message Handler', () => {
    it('should ack when given proper message', async () => {
      const msg = getMessage(this.exampleImaging);
      await this.mq._msgHandler(msg);

      expect(this.algorithmSpy).to.have.been.calledOnceWithExactly(this.exampleImaging);
      // eslint-disable-next-line max-len
      expect(this.publishStub).to.have.been.calledOnceWith(Sinon.match.any, Sinon.match.any, Buffer.from(JSON.stringify(this.exampleDiagnosis)), Sinon.match.any);
      expect(this.ackStub).to.have.been.calledOnceWithExactly(msg);
      // eslint-disable-next-line no-unused-expressions
      expect(this.rejectStub).to.have.not.been.called;
    });

    it('should reject with no requeue when given improper message', async () => {
      const msg = getMessage(this.badImaging);
      await this.mq._msgHandler(msg);

      // eslint-disable-next-line no-unused-expressions
      expect(this.publishStub).to.have.not.been.called;
      // eslint-disable-next-line no-unused-expressions
      expect(this.ackStub).to.have.not.been.called;
      expect(this.rejectStub).to.have.been.calledOnceWithExactly(msg, false);
    });

    it('should reject with no requeue when algorithm fails', async () => {
      this.algorithmSpy.restore();
      const algorithmStub = Sinon.stub(this.algorithm, 'run').throws();

      const msg = getMessage(this.exampleImaging);
      await this.mq._msgHandler(msg);

      expect(algorithmStub).to.have.been.calledOnceWithExactly(this.exampleImaging);
      // eslint-disable-next-line no-unused-expressions
      expect(this.publishStub).to.have.not.been.called;
      // eslint-disable-next-line no-unused-expressions
      expect(this.ackStub).to.have.not.been.called;
      expect(this.rejectStub).to.have.been.calledOnceWithExactly(msg, false);
      algorithmStub.restore();
    });

    it('should reject with requeue proper message when fails to publish diagnosis', async () => {
      this.publishStub.restore();
      this.publishStub = Sinon.stub(this.channel, 'publish').throws();

      const msg = getMessage(this.exampleImaging);
      await this.mq._msgHandler(msg);

      expect(this.algorithmSpy).to.have.been.calledOnceWithExactly(this.exampleImaging);
      // eslint-disable-next-line max-len
      expect(this.publishStub).to.have.been.calledOnceWith(Sinon.match.any, Sinon.match.any, Buffer.from(JSON.stringify(this.exampleDiagnosis)), Sinon.match.any);
      // eslint-disable-next-line no-unused-expressions
      expect(this.ackStub).to.have.not.been.called;
      expect(this.rejectStub).to.have.been.calledOnceWithExactly(msg, true);
    });
  });
});
