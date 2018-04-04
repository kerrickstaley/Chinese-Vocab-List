# available targets:
# - regen: regenerates the file chinese_vocab_list.yaml
# - install: installs the library locally

.PHONY: regen
regen: chinese_vocab_list.yaml

.PHONY: install
install: build/chinese_vocab_list/__init__.py build/chinese_vocab_list/models.py build/setup.py \
		build/chinese_vocab_list/chinese_vocab_list.yaml
	cd build; sudo python3 setup.py install

build/chinese_vocab_list/__init__.py: src/vocab_list.py
	mkdir -p build/chinese_vocab_list/
	cp "$<" "$@"

build/chinese_vocab_list/models.py: src/models.py
	mkdir -p build/chinese_vocab_list/
	cp "$<" "$@"

build/chinese_vocab_list/chinese_vocab_list.yaml: chinese_vocab_list.yaml
	mkdir -p build/chinese_vocab_list
	cp "$<" "$@"

build/setup.py: setup.py
	mkdir -p build
	cp "$<" "$@"

chinese_vocab_list.yaml: src/*
	python3 src/build_initial_list.py > "$@"
