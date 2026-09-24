class BtpGuard < Formula
  include Language::Python::Virtualenv

  desc "Deterministic AST execution gating, secret scrubbing, and receipts for AI agents"
  homepage "https://bartholomew.info"
  url "https://files.pythonhosted.org/packages/source/b/btp-guard/btp_guard-5.4.20.tar.gz"
  version "5.4.20"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "Bartholomew", shell_output("#{bin}/btp-guard version")
  end
end
