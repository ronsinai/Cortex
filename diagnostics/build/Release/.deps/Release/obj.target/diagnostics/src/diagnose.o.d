cmd_Release/obj.target/diagnostics/src/diagnose.o := g++ -o Release/obj.target/diagnostics/src/diagnose.o ../src/diagnose.cpp '-DNODE_GYP_MODULE_NAME=diagnostics' '-DUSING_UV_SHARED=1' '-DUSING_V8_SHARED=1' '-DV8_DEPRECATION_WARNINGS=1' '-DV8_DEPRECATION_WARNINGS' '-DV8_IMMINENT_DEPRECATION_WARNINGS' '-D_LARGEFILE_SOURCE' '-D_FILE_OFFSET_BITS=64' '-D__STDC_FORMAT_MACROS' '-DOPENSSL_NO_PINSHARED' '-DOPENSSL_THREADS' '-DNAPI_DISABLE_CPP_EXCEPTIONS' '-DBUILDING_NODE_EXTENSION' -I/home/osboxes/.cache/node-gyp/14.15.3/include/node -I/home/osboxes/.cache/node-gyp/14.15.3/src -I/home/osboxes/.cache/node-gyp/14.15.3/deps/openssl/config -I/home/osboxes/.cache/node-gyp/14.15.3/deps/openssl/openssl/include -I/home/osboxes/.cache/node-gyp/14.15.3/deps/uv/include -I/home/osboxes/.cache/node-gyp/14.15.3/deps/zlib -I/home/osboxes/.cache/node-gyp/14.15.3/deps/v8/include -I/home/osboxes/Workspace/Diagnostics/node_modules/node-addon-api  -fPIC -pthread -Wall -Wextra -Wno-unused-parameter -m64 -O3 -fno-omit-frame-pointer -fno-rtti -std=gnu++1y -MMD -MF ./Release/.deps/Release/obj.target/diagnostics/src/diagnose.o.d.raw   -c
Release/obj.target/diagnostics/src/diagnose.o: ../src/diagnose.cpp \
 ../src/diagnose.h ../src/diagnosis.h ../src/algorithms/ct.h \
 ../src/algorithms/../imaging.h ../src/algorithms/../metadata.h \
 ../src/algorithms/mri.h ../src/algorithms/us.h ../src/algorithms/xrays.h \
 ../src/imaging.h ../src/metadata.h
../src/diagnose.cpp:
../src/diagnose.h:
../src/diagnosis.h:
../src/algorithms/ct.h:
../src/algorithms/../imaging.h:
../src/algorithms/../metadata.h:
../src/algorithms/mri.h:
../src/algorithms/us.h:
../src/algorithms/xrays.h:
../src/imaging.h:
../src/metadata.h:
