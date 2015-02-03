
import sys
sys.path.append('..')
import hashlib
import locale
from random import shuffle
import time
import unittest

from CppBlockUtils import HDWalletCrypto
from armoryengine.ArmoryUtils import *
from armoryengine.BinaryPacker import *
from armoryengine.BinaryUnpacker import *
import armoryengine.ArmoryUtils
from armoryengine import ArmoryUtils
from armoryengine import ArmoryUtils
from armoryengine.ConstructedScript import *

############# Various constants we wish to use throughout the tests.
# Master key derived from the 2nd BIP32 test vector + child key 0.
BIP32MasterPubKey2        = hex_to_binary(
   "04cbcaa9 c98c877a 26977d00 825c956a 238e8ddd fbd322cc e4f74b0b 5bd6ace4"
   "a77bd330 5d363c26 f82c1e41 c667e4b3 561c06c6 0a2104d2 b548e6dd 059056aa 51")
BIP32MasterPubKey2Comp    = hex_to_binary(
   "03cbcaa9 c98c877a 26977d00 825c956a 238e8ddd fbd322cc e4f74b0b 5bd6ace4 a7")
BIP32MasterPubKey2_D1     = hex_to_binary(
   "04fc9e5a f0ac8d9b 3cecfe2a 888e2117 ba3d089d 8585886c 9c826b6b 22a98d12"
   "ea67a505 38b6f7d8 b5f7a1cc 657efd26 7cde8cc1 d8c0451d 1340a0fb 36427775 44")
BIP32MasterPubKey2Comp_D1 = hex_to_binary(
   "02fc9e5a f0ac8d9b 3cecfe2a 888e2117 ba3d089d 8585886c 9c826b6b 22a98d12 ea")
BIP32MasterPubKey2Multiplier = hex_to_binary(
   "60e3739c c2c3950b 7c4d7f32 cc503e13 b996d0f7 a45623d0 a914e1ef a7f811e0")

# PKS serializations based on BIP32MasterPubKey2.
PKS1Chksum_Uncomp_v0 = hex_to_binary(
   "00004041 04cbcaa9 c98c877a 26977d00 825c956a 238e8ddd fbd322cc e4f74b0b"
   "5bd6ace4 a77bd330 5d363c26 f82c1e41 c667e4b3 561c06c6 0a2104d2 b548e6dd"
   "059056aa 513a6dee 2c")
PKS1NoChksum_Comp_v0 = hex_to_binary(
   "00000221 03cbcaa9 c98c877a 26977d00 825c956a 238e8ddd fbd322cc e4f74b0b"
   "5bd6ace4 a7")

# CS serializations based on BIP32MasterPubKey2.
CS1Chksum_Uncomp_v0 = hex_to_binary(
   "00000206 76a9ff01 88ac0145 00000441 04cbcaa9 c98c877a 26977d00 825c956a"
   "238e8ddd fbd322cc e4f74b0b 5bd6ace4 a77bd330 5d363c26 f82c1e41 c667e4b3"
   "561c06c6 0a2104d2 b548e6dd 059056aa 51142038 ce")
CS1NoChksum_Comp_v0 = hex_to_binary(
   "00000006 76a9ff01 88ac0125 00000621 03cbcaa9 c98c877a 26977d00 825c956a"
   "238e8ddd fbd322cc e4f74b0b 5bd6ace4 a7")
CS2Chksum_Comp_v0 = hex_to_binary( # Multisig
   "00000305 52ff0252 ae022500 00022103 cbcaa9c9 8c877a26 977d0082 5c956a23"
   "8e8dddfb d322cce4 f74b0b5b d6ace4a7 25000002 2102fc9e 5af0ac8d 9b3cecfe"
   "2a888e21 17ba3d08 9d858588 6c9c826b 6b22a98d 12ea87d6 e378")

# PKRP serializations based on BIP32MasterPubKey2.
PKRP1_v0 = hex_to_binary(
   "00012060 e3739cc2 c3950b7c 4d7f32cc 503e13b9 96d0f7a4 5623d0a9 14e1efa7"
   "f811e0")
PKRP2_v0 = hex_to_binary(
   "00022060 e3739cc2 c3950b7c 4d7f32cc 503e13b9 96d0f7a4 5623d0a9 14e1efa7"
   "f811e020 60e3739c c2c3950b 7c4d7f32 cc503e13 b996d0f7 a45623d0 a914e1ef"
   "a7f811e0")

# SRP serializations based on BIP32MasterPubKey2.
SRP1_v0 = hex_to_binary(
   "00010001 2060e373 9cc2c395 0b7c4d7f 32cc503e 13b996d0 f7a45623 d0a914e1"
   "efa7f811 e0")
SRP2_v0 = hex_to_binary(
   "00020001 2060e373 9cc2c395 0b7c4d7f 32cc503e 13b996d0 f7a45623 d0a914e1"
   "efa7f811 e0000120 60e3739c c2c3950b 7c4d7f32 cc503e13 b996d0f7 a45623d0"
   "a914e1ef a7f811e0")


################################################################################
class PKSClassTests(unittest.TestCase):
   # Use serialize/unserialize to confirm that the data struct is correctly
   # formed and can be correctly formed.
   def testSerialization(self):
      # PKS1 with a checksum & uncompressed key.
      pks1ChksumPres = PublicKeySource()
      pks1ChksumPres.initialize(False, False, False, False, False,
                                BIP32MasterPubKey2, True)
      stringPKS1ChksumPres = pks1ChksumPres.serialize()
      self.assertEqual(binary_to_hex(stringPKS1ChksumPres),
                       binary_to_hex(PKS1Chksum_Uncomp_v0))

      # PKS1 without a checksum & with a compressed key.
      pks1NoChksum = PublicKeySource()
      pks1NoChksum.initialize(False, False, False, False, False,
                              BIP32MasterPubKey2Comp, False)
      stringPKS1NoChksum = pks1NoChksum.serialize()
      self.assertEqual(binary_to_hex(stringPKS1NoChksum),
                       binary_to_hex(PKS1NoChksum_Comp_v0))

      # Unserialize and re-serialize to confirm unserialize works.
      pks1ChksumPres_unser = PublicKeySource().unserialize(PKS1Chksum_Uncomp_v0)
      pks1NoChksum_unser = PublicKeySource().unserialize(PKS1NoChksum_Comp_v0)
      stringPKS1Chksum_unser = pks1ChksumPres_unser.serialize()
      stringPKS1NoChksum_unser = pks1NoChksum_unser.serialize()
      self.assertEqual(binary_to_hex(stringPKS1Chksum_unser),
                       binary_to_hex(PKS1Chksum_Uncomp_v0))
      self.assertEqual(binary_to_hex(stringPKS1NoChksum_unser),
                       binary_to_hex(PKS1NoChksum_Comp_v0))


################################################################################
class CSClassTests(unittest.TestCase):
   # Use serialize/unserialize to confirm that the data struct is correctly
   # formed and can be correctly formed.
   def testSerialization(self):
      # CS1 w/ a checksum - Pre-built P2PKH
      cs1ChksumPres = ConstructedScript().StandardP2PKHConstructed(BIP32MasterPubKey2)
      stringCS1ChksumPres = cs1ChksumPres.serialize()
      self.assertEqual(binary_to_hex(stringCS1ChksumPres),
                       binary_to_hex(CS1Chksum_Uncomp_v0))

      # CS2 w/ a checksum - Pre-built multisig
      testKeyList = [BIP32MasterPubKey2Comp, BIP32MasterPubKey2Comp_D1]
      cs2ChksumPres = ConstructedScript().StandardMultisigConstructed(2, testKeyList)
      stringCS2ChksumPres = cs2ChksumPres.serialize()
      self.assertEqual(binary_to_hex(stringCS2ChksumPres),
                       binary_to_hex(CS2Chksum_Comp_v0))

      # Unserialize and re-serialize to confirm unserialize works.
      cs1ChksumPres_unser = ConstructedScript().unserialize(CS1Chksum_Uncomp_v0)
      cs2ChksumPres_unser = ConstructedScript().unserialize(CS2Chksum_Comp_v0)
      stringCS1Chksum_unser = cs1ChksumPres_unser.serialize()
      stringCS2Chksum_unser = cs2ChksumPres_unser.serialize()
      self.assertEqual(binary_to_hex(stringCS1Chksum_unser),
                       binary_to_hex(CS1Chksum_Uncomp_v0))
      self.assertEqual(binary_to_hex(stringCS2Chksum_unser),
                       binary_to_hex(CS2Chksum_Comp_v0))


################################################################################
class PKRPClassTests(unittest.TestCase):
   # Use serialize/unserialize to confirm that the data struct is correctly
   # formed and can be correctly formed.
   def testSerialization(self):
      # 1 multiplier.
      pkrp1 = PublicKeyRelationshipProof()
      pkrp1.initialize([BIP32MasterPubKey2Multiplier])
      stringPKRP1 = pkrp1.serialize()
      self.assertEqual(binary_to_hex(stringPKRP1),
                       binary_to_hex(PKRP1_v0))

      # 2 multipliers. Both mults are the same. This test just confirms that the
      # serialization code works.
      pkrp2 = PublicKeyRelationshipProof()
      pkrp2.initialize([BIP32MasterPubKey2Multiplier,
                        BIP32MasterPubKey2Multiplier])
      stringPKRP2 = pkrp2.serialize()
      self.assertEqual(binary_to_hex(stringPKRP2),
                       binary_to_hex(PKRP2_v0))

      # Unserialize and re-serialize to confirm unserialize works.
      pkrp1_unser = PublicKeyRelationshipProof().unserialize(PKRP1_v0)
      pkrp2_unser = PublicKeyRelationshipProof().unserialize(PKRP2_v0)
      stringPKRP1_unser = pkrp1_unser.serialize()
      stringPKRP2_unser = pkrp2_unser.serialize()
      self.assertEqual(binary_to_hex(stringPKRP1_unser),
                       binary_to_hex(PKRP1_v0))
      self.assertEqual(binary_to_hex(stringPKRP2_unser),
                       binary_to_hex(PKRP2_v0))


################################################################################
class SRPClassTests(unittest.TestCase):
   # Use serialize/unserialize to confirm that the data struct is correctly
   # formed and can be correctly formed.
   def testSerialization(self):
      # 1 PKRP.
      pkrp1 = PublicKeyRelationshipProof()
      pkrp1.initialize([BIP32MasterPubKey2Multiplier])
      srp1 = ScriptRelationshipProof()
      srp1.initialize([pkrp1])
      stringSRP1 = srp1.serialize()
      self.assertEqual(binary_to_hex(stringSRP1),
                       binary_to_hex(SRP1_v0))

      # 2 PKRPs. Both PKRPs are the same. This test just confirms that the
      # serialization code works.
      srp2 = ScriptRelationshipProof()
      srp2.initialize([pkrp1, pkrp1])
      stringSRP2 = srp2.serialize()
      self.assertEqual(binary_to_hex(stringSRP2),
                       binary_to_hex(SRP2_v0))

      # Unserialize and re-serialize to confirm unserialize works.
#      srp1_unser = PublicKeyRelationshipProof().unserialize(SRP1_v0)
#      srp2_unser = PublicKeyRelationshipProof().unserialize(SRP2_v0)
#      stringSRP1_unser = srp1_unser.serialize()
#      stringSRP2_unser = srp2_unser.serialize()
#      self.assertEqual(binary_to_hex(stringSRP1_unser),
#                       binary_to_hex(SRP1_v0))
#      self.assertEqual(binary_to_hex(stringSRP2_unser),
#                       binary_to_hex(SRP2_v0))


################################################################################
class DerivationTests(unittest.TestCase):
   # Confirm that BIP32 multipliers can be obtained from C++ and can be used to
   # create keys that match the keys directly derived via BIP32.
   def testBIP32Derivation(self):
      fakeRootSeed = SecureBinaryData('\xf1'*32)
      masterExtPrv = HDWalletCrypto().convertSeedToMasterKey(fakeRootSeed)
      sbdPubKey = masterExtPrv.getPublicKey()
      sbdChain  = masterExtPrv.getChaincode()

      # Get the final pub key and the multiplier proofs, then confirm that we
      # can reverse engineer the final key with the proofs and the root pub key.
      # Note that the proofs will be based on a compressed root pub key.
      finalPub, multProof = DeriveBip32PublicKeyWithProof(sbdPubKey.toBinStr(),
                                                          sbdChain.toBinStr(),
                                                          [2, 12, 37])
      final1 = ApplyProofToRootKey(sbdPubKey.toBinStr(), multProof)
      final1_alt = ApplyProofToRootKey(sbdPubKey.toBinStr(), multProof, finalPub)
      self.assertEqual(final1, finalPub)
      self.assertEqual(final1, final1_alt)

      # Confirm that we can get the 1st derived key from the BIP32 test vector's
      # second key.
      bip32Seed2            = SecureBinaryData(hex_to_binary(
         "fffcf9f6 f3f0edea e7e4e1de dbd8d5d2 cfccc9c6 c3c0bdba b7b4b1ae"
         "aba8a5a2 9f9c9996 93908d8a 8784817e 7b787572 6f6c6966 63605d5a"
         "5754514e 4b484542"))
      masterExtPrv2         = HDWalletCrypto().convertSeedToMasterKey(bip32Seed2)
      sbdPubKey2            = masterExtPrv2.getPublicKey()
      sbdChain2             = masterExtPrv2.getChaincode()
      finalPub2, multProof2 = DeriveBip32PublicKeyWithProof(sbdPubKey2.toBinStr(),
                                                            sbdChain2.toBinStr(),
                                                            [0])
      self.assertEqual(finalPub2, BIP32MasterPubKey2Comp_D1)


if __name__ == "__main__":
   unittest.main()
