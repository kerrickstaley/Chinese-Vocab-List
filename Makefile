# available targets:
# - regen: regenerates the file chinese_vocab_list.yaml
# - install: installs the library locally

.PHONY: regen
regen: chinese_vocab_list.yaml

.PHONY: install
install: chinesevocablist/* chinesevocablist/vocab_list_data.py
	python3 setup.py install --user

chinesevocablist/vocab_list_data.py: chinesevocablist/__init__.py \
		chinesevocablist/models.py src/generate_vocab_list_data.py chinese_vocab_list.yaml
	PYTHONPATH="." python3 src/generate_vocab_list_data.py > "$@"

chinese_vocab_list.yaml: src/* reference_files/* contrib_files/* chinesevocablist/__init__.py \
		chinesevocablist/models.py
	$(eval tempfile := $(shell mktemp))
	PYTHONPATH="." python3 src/build_initial_list.py > "${tempfile}"
	cp "${tempfile}" "$@"
