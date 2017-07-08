.PHONY: install
install: build/chinese_vocab_list/__init__.py build/chinese_vocab_list/models.py build/setup.py \
		build/chinese_vocab_list/chinese_vocab_list.yaml
	cd build; sudo python3 setup.py install

build/chinese_vocab_list/__init__.py: src/vocab_list.py
	mkdir -p build/chinese_vocab_list/
	cp src/vocab_list.py build/chinese_vocab_list/__init__.py

build/chinese_vocab_list/models.py: src/models.py
	mkdir -p build/chinese_vocab_list/
	cp src/models.py build/chinese_vocab_list/models.py

build/setup.py: setup.py
	mkdir -p build
	cp setup.py build/setup.py

build/chinese_vocab_list/chinese_vocab_list.yaml: src/*
	mkdir -p build
	python3 src/build_initial_list.py > build/chinese_vocab_list/chinese_vocab_list.yaml
