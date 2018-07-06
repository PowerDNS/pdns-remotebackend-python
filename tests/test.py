import json
import unittest
import re
import sys

from subprocess import PIPE, Popen


class pipetest(unittest.TestCase):
    def test_pipe_abi_pipe(self):
        sub = Popen(["/usr/bin/env", "python", "src/pipe_abi.py", "pipe"],
                    stdin=PIPE, stdout=PIPE, stderr=sys.stderr,
                    close_fds=True, shell=False)
        (writer, reader) = (sub.stdin, sub.stdout)
        writer.write("HELO\t1\n".encode("utf-8"))
        writer.flush()
        sub.poll()
        line = reader.readline().decode("utf-8")
        assert(re.match("^OK\t", line))
        writer.write("Q\ttest.com\tIN\tSOA\t-1\t127.0.0.1\n".encode("utf-8"))
        writer.flush()
        line = reader.readline().decode("utf-8")
        print(line)
        assert(re.match("^DATA\ttest.com\tIN\tSOA\t300\t-1\t"
                        "sns.dns.icann.org. noc.dns.icann.org. "
                        "2013073082 7200 3600 1209600 3600",
                        line))
        writer.flush()
        line = reader.readline().decode("utf-8")
        assert(re.match("^END", line))
        writer.write(
            "Q\tinvalid.test\tIN\tSOA\t-1\t127.0.0.1\n".encode("utf-8")
        )
        writer.flush()
        line = reader.readline().decode("utf-8")
        assert(re.match("^FAIL", line))
        sub.stdout.close()
        sub.stdin.close()
        sub.kill()
        sub.wait()

    def test_pipe_abi_remote(self):
        sub = Popen(["/usr/bin/env", "python", "src/pipe_abi.py", "remote"],
                    stdin=PIPE, stdout=PIPE, stderr=sys.stderr,
                    close_fds=True, shell=False)
        (writer, reader) = (sub.stdin, sub.stdout)
        writer.write(json.dumps({
            "method": "initialize",
            "parameters": {
                "timeout": 2000
            }
        }).encode("utf-8"))
        writer.write("\n".encode("utf-8"))
        writer.flush()
        sub.poll()
        line = reader.readline().decode("utf-8")
        resp = json.loads(line)
        assert(resp["result"] == True)
        writer.write(json.dumps({
            "method": "lookup",
            "parameters": {
                "qname": "test.com",
                "qtype": "SOA"
            }
        }).encode("utf-8"))
        writer.write("\n".encode("utf-8"))
        writer.flush()
        resp = json.loads(reader.readline().decode("utf-8"))
        assert(resp["result"][0]["qname"] == "test.com")
        sub.stdout.close()
        sub.stdin.close()
        sub.kill()
        sub.wait()

if __name__ == '__main__':
        unittest.main()
