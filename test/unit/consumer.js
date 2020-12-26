const Chai = require('chai');
const Nconf = require('nconf');
const Sinon = require('sinon');
const SinonChai = require('sinon-chai');
const { ValidationError } = require('joi');

Chai.use(SinonChai);
const { expect } = Chai;

const exampleImaging = require('../data/imaging');
const { getMessage } = require('../utils/mq');

describe('Consumer', () => {
  before(() => {
    this.requeue_on_reject = false;

    this.exampleImaging = exampleImaging;
    this.badImaging = { _id: 'partial' };

    const { _id, type } = exampleImaging;
    this.exampleDiagnosis = { imagingId: _id, imagingType: type, diagnosis: Nconf.get('AMQP_QUEUE') };

    this.mq = global.consumerInstance.mq;
    this.channel = this.mq.channel;
    this.algorithm = this.mq.algorithm;
  });

  beforeEach(() => {
    this.algorithmSpy = Sinon.spy(this.algorithm, 'run');

    this.ackStub = Sinon.stub(this.channel, 'ack');
    this.rejectStub = Sinon.stub(this.channel, 'reject');
  });

  afterEach(() => {
    this.algorithmSpy.restore();

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
    it('should ack when given proper message', () => {
      const msg = getMessage(this.exampleImaging);
      this.mq._msgHandler(msg);

      expect(this.algorithmSpy).to.have.been.calledOnceWithExactly(this.exampleImaging);
      expect(this.ackStub).to.have.been.calledOnceWithExactly(msg);
      // eslint-disable-next-line no-unused-expressions
      expect(this.rejectStub).to.have.not.been.called;
    });

    it('should reject with no requeue when given improper message', () => {
      const msg = getMessage(this.badImaging);
      this.mq._msgHandler(msg);

      // eslint-disable-next-line no-unused-expressions
      expect(this.ackStub).to.have.not.been.called;
      expect(this.rejectStub).to.have.been.calledOnceWithExactly(msg, this.requeue_on_reject);
    });

    it('should reject with no requeue when algorithm fails', () => {
      this.algorithmSpy.restore();
      const algorithmStub = Sinon.stub(this.algorithm, 'run').throws();

      const msg = getMessage(this.exampleImaging);
      this.mq._msgHandler(msg);

      expect(algorithmStub).to.have.been.calledOnceWithExactly(this.exampleImaging);
      // eslint-disable-next-line no-unused-expressions
      expect(this.ackStub).to.have.not.been.called;
      expect(this.rejectStub).to.have.been.calledOnceWithExactly(msg, this.requeue_on_reject);
      algorithmStub.restore();
    });
  });
});
