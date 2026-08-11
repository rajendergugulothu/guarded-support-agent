# Guarded Support Agent — common commands
# Mock LLM by default (no key). Add ANTHROPIC_API_KEY for the real judge + planner,
# and SDR_ENV=prod for fail-closed behavior.

.PHONY: pipeline metrics cases suite publish prod-demo demo test clean

pipeline:    ## run tickets end to end: plan -> guardrail -> resolve / escalate
	python -m support_agent.pipeline

metrics:     ## operational metrics from the last run
	python -m support_agent.metrics

cases:       ## (re)generate the labeled trajectory dataset
	python -m eval_suite.generate

suite: cases ## run the trajectory evaluation suite
	python -m eval_suite.run

publish:     ## write real eval numbers from results.json into the docs
	python -m eval_suite.publish

prod-demo:   ## fail-closed: unavailable judge -> escalate instead of act
	SDR_ENV=prod python -m support_agent.pipeline

test:        ## run unit tests (pip install pytest first)
	pytest -q

demo: pipeline suite metrics   ## the full story end to end

clean:
	rm -rf runs eval_suite/results.json __pycache__ */__pycache__ */*/__pycache__
