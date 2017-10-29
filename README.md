# NAT64Check Zaphod back-end
This is the back-end system for Zaphod.

NAT64Check consists of three layers:

- Zaphod: the president of the NAT64Check universe
  - Front-end: the user interface for scheduling tests and looking up results
  - Back-end: the API where tests are dispatched to one or more Trillians
- Trillian: the coordinator of a test-run and master of Marvins
- Marvin: the menial worker performing a part of a test

There are multiple Trillians, each coordinating tests in a part of the world.
Each Trillian controls multiple Marvins. Each Marvin is connected to a different
kind of network (IPv4-only, NAT64 etc.) to test a website under different
circumstances.

There is only one Zaphod, controlling all Trillians.
