# available targets:
# - regen: regenerates the file chinese_vocab_list.yaml
# - install: installs the library locally

.PHONY: regen
regen: chinese_vocab_list.yaml

.PHONY: install
install: build/chinese_vocab_list/__init__.py build/chinese_vocab_list/models.py \
    build/chinese_vocab_list/vocab_list_data.py build/setup.py
	cd build; sudo python3 setup.py install

build/chinese_vocab_list/__init__.py: chinese_vocab_list/__init__.py
	mkdir -p build/chinese_vocab_list/
	cp "$<" "$@"

build/chinese_vocab_list/models.py: chinese_vocab_list/models.py
	mkdir -p build/chinese_vocab_list/
	cp "$<" "$@"

build/chinese_vocab_list/vocab_list_data.py: chinese_vocab_list/* chinese_vocab_list.yaml
	mkdir -p build/chinese_vocab_list/
	PYTHONPATH="." python3 src/generate_vocab_list_data.py > "$@"

build/setup.py: setup.py
	mkdir -p build
	cp "$<" "$@"

chinese_vocab_list.yaml: src/* reference_files/* contrib_files/* chinese_vocab_list/*
	$(eval tempfile := $(shell mktemp))
	PYTHONPATH="." python3 src/build_initial_list.py > "${tempfile}"
	cp "${tempfile}" "$@"
