import os

data = (
    ('InitTemp', '/AccountStore.cpp:64'),
    ('PutBlock', '/BlockStorage.cpp:50'),
    ('PutBlock', '/BlockStorage.cpp:53'),
    ('GetFromFile', '/GetTxnFromFile.h:91'),
    ('DeserializeDelta', 'AccountStore.cpp:143'),
    ('MoveUpdatesToDisk', 'AccountStore.cpp:180'),
    ('CommitTemp', 'AccountStore.cpp:358'),
    ('PutMetadata', 'BlockStorage.cpp:498'),
    ('PutDSCommittee', 'BlockStorage.cpp:519'),
    ('PutDSCommittee', 'BlockStorage.cpp:532'),
    ('PutDSCommittee', 'BlockStorage.cpp:550'),
    ('PutShardStructure', 'BlockStorage.cpp:593'),
    ('PutShardStructure', 'BlockStorage.cpp:606'),
    ('PutShardStructure', 'BlockStorage.cpp:621'),
    ('PutStateDelta', 'BlockStorage.cpp:652'),
    ('PutStateDelta', 'BlockStorage.cpp:662'),
    ('PutDiagnosticDataNod', 'BlockStorage.cpp:680'),
    ('ResetDB', 'BlockStorage.cpp:938'),
    ('operator()', 'GetTxnFromFile.h:111'),
    ('convertJsontoTx', 'ONConversion.cpp:180'),
    ('checkJsonTx', 'ONConversion.cpp:253'),
    ('UpdateDSBlockRand', 'ator/Mediator.cpp:61'),
    ('UpdateTxBlockRand', 'ator/Mediator.cpp:82'),
    ('IsMicroBlockTxRootHa', 'ckProcessing.cpp:105'),
    ('IsMicroBlockTxRootHa', 'ckProcessing.cpp:113'),
    ('VerifyDSBlockCoSigna', 'ckProcessing.cpp:119'),
    ('LoadUnavailableMicro', 'ckProcessing.cpp:132'),
    ('LogReceivedDSBlockDe', 'ckProcessing.cpp:173'),
    ('LogReceivedDSBlockDe', 'ckProcessing.cpp:174'),
    ('LogReceivedDSBlockDe', 'ckProcessing.cpp:175'),
    ('LogReceivedDSBlockDe', 'ckProcessing.cpp:176'),
    ('LogReceivedDSBlockDe', 'ckProcessing.cpp:178'),
    ('LogReceivedDSBlockDe', 'ckProcessing.cpp:182'),
    ('RemoveTxRootHashFrom', 'ckProcessing.cpp:210'),
    ('RemoveTxRootHashFrom', 'ckProcessing.cpp:215'),
    ('RemoveTxRootHashFrom', 'ckProcessing.cpp:222'),
    ('VerifyFinalBlockCoSi', 'ckProcessing.cpp:232'),
    ('ProcessVCDSBlocksMes', 'ckProcessing.cpp:325'),
    ('ProcessVCDSBlocksMes', 'ckProcessing.cpp:334'),
    ('CheckStateRoot', 'ckProcessing.cpp:512'),
    ('ProcessVCDSBlocksMes', 'ckProcessing.cpp:513'),
    ('ProcessFinalBlock', 'ckProcessing.cpp:529'),
    ('ProcessFinalBlock', 'ckProcessing.cpp:582'),
    ('ProcessVCDSBlocksMes', 'ckProcessing.cpp:664'),
    ('ProcessFinalBlock', 'ckProcessing.cpp:667'),
    ('ProcessFinalBlock', 'ckProcessing.cpp:698'),
    ('ProcessStateDeltaFro', 'ckProcessing.cpp:788'),
    ('ProcessStateDeltaFro', 'ckProcessing.cpp:794'),
    ('ProcessStateDeltaFro', 'ckProcessing.cpp:799'),
    ('ProcessStateDeltaFro', 'ckProcessing.cpp:819'),
    ('CommitForwardedTrans', 'ckProcessing.cpp:836'),
    ('CommitForwardedTrans', 'ckProcessing.cpp:850'),
    ('DeleteEntryFromFwdin', 'ckProcessing.cpp:855'),
    ('DeleteEntryFromFwdin', 'ckProcessing.cpp:865'),
    ('DeleteEntryFromFwdin', 'ckProcessing.cpp:875'),
    ('ProcessMBnForwardTra', 'ckProcessing.cpp:907'),
    ('ProcessMBnForwardTra', 'ckProcessing.cpp:945'),
    ('ProcessMBnForwardTra', 'ckProcessing.cpp:947'),
    ('ProcessMBnForwardTra', 'ckProcessing.cpp:949'),
    ('ProcessMBnForwardTra', 'ckProcessing.cpp:980'),
    ('ProcessMBnForwardTra', 'ckProcessing.cpp:982'),
    ('ProcessMBnForwardTra', 'ckProcessing.cpp:999'),
    ('GetAccountStoreDelta', 'e/Messenger.cpp:2525'),
    ('GetNodeVCDSBlocksMes', 'e/Messenger.cpp:4167'),
    ('GetNodeFinalBlock', 'e/Messenger.cpp:4222'),
    ('GetNodeMBnForwardTra', 'e/Messenger.cpp:4276'),
    ('GetNodeMBnForwardTra', 'e/Messenger.cpp:4298'),
    ('SetNodeForwardTxnBlo', 'e/Messenger.cpp:4340'),
    ('SetNodeForwardTxnBlo', 'e/Messenger.cpp:4410'),
    ('GetLookupSetRaiseSta', 'e/Messenger.cpp:5743'),
    ('CreateTransaction', 'erver/Server.cpp:160'),
    ('GetTransaction', 'erver/Server.cpp:321'),
    ('GetLatestDsBlock', 'erver/Server.cpp:402'),
    ('GetLatestDsBlock', 'erver/Server.cpp:407'),
    ('GetBalance', 'erver/Server.cpp:424'),
    ('GetBalance', 'erver/Server.cpp:446'),
    ('GetSmartContractStat', 'erver/Server.cpp:462'),
    ('GetSmartContractInit', 'erver/Server.cpp:498'),
    ('GetSmartContractCode', 'erver/Server.cpp:533'),
    ('GetSmartContracts', 'erver/Server.cpp:569'),
    ('GetNumPeers', 'erver/Server.cpp:650'),
    ('GetNumTxBlocks', 'erver/Server.cpp:657'),
    ('GetNumDSBlocks', 'erver/Server.cpp:663'),
    ('GetNumTransactions', 'erver/Server.cpp:677'),
    ('GetTransactionRate', 'erver/Server.cpp:711'),
    ('GetTransactionRate', 'erver/Server.cpp:733'),
    ('GetDSBlockRate', 'erver/Server.cpp:765'),
    ('GetTxBlockRate', 'erver/Server.cpp:801'),
    ('GetCurrentMiniEpoch', 'erver/Server.cpp:833'),
    ('GetCurrentDSEpoch', 'erver/Server.cpp:839'),
    ('DSBlockListing', 'erver/Server.cpp:846'),
    ('TxBlockListing', 'erver/Server.cpp:938'),
    ('GetDSLeader', 'ibNode/Node.cpp:2115'),
    ('GetDSLeader', 'ibNode/Node.cpp:2116'),
    ('GetDSLeader', 'ibNode/Node.cpp:2117'),
    ('GetDSLeader', 'ibNode/Node.cpp:2118'),
    ('CommitMBnForwardedTr', 'kProcessing.cpp:1028'),
    ('AddBlockLink', 'lockLinkChain.cpp:76'),
    ('AddBlockLink', 'lockLinkChain.cpp:77'),
    ('AddBlockLink', 'lockLinkChain.cpp:78'),
    ('AddBlockLink', 'lockLinkChain.cpp:79'),
    ('GetBroadcastList', 'n/Broadcastable.h:33'),
    ('GetBroadcastList', 'n/Broadcastable.h:44'),
    ('StoreDSBlockToDisk', 'ockProcessing.cpp:60'),
    ('StoreState', 'ockProcessing.cpp:63'),
    ('StoreDSBlockToDisk', 'ockProcessing.cpp:63'),
    ('StoreDSBlockToDisk', 'ockProcessing.cpp:65'),
    ('StoreDSBlockToDisk', 'ockProcessing.cpp:67'),
    ('StoreFinalBlock', 'ockProcessing.cpp:68'),
    ('StoreDSBlockToDisk', 'ockProcessing.cpp:68'),
    ('StoreFinalBlock', 'ockProcessing.cpp:77'),
    ('UpdateDSCommiteeComp', 'ockProcessing.cpp:93'),
    ('AddMicroBlockToStora', 'okup/Lookup.cpp:1320'),
    ('ProcessRaiseStartPoW', 'okup/Lookup.cpp:2433'),
    ('ProcessRaiseStartPoW', 'okup/Lookup.cpp:2488'),
    ('ProcessRaiseStartPoW', 'okup/Lookup.cpp:2501'),
    ('Execute', 'okup/Lookup.cpp:3158'),
    ('SenderTxnBatchThread', 'okup/Lookup.cpp:3261'),
    ('SendTxnPacketToNodes', 'okup/Lookup.cpp:3292'),
    ('SendTxnPacketToNodes', 'okup/Lookup.cpp:3319'),
    ('SendTxnPacketToNodes', 'okup/Lookup.cpp:3322'),
    ('SendTxnPacketToNodes', 'okup/Lookup.cpp:3346'),
    ('SendTxnPacketToNodes', 'okup/Lookup.cpp:3359'),
    ('SendTxnPacketToNodes', 'okup/Lookup.cpp:3402'),
    ('GenTxnToSend', 'ookup/Lookup.cpp:323'),
    ('GenTxnToSend', 'ookup/Lookup.cpp:355'),
    ('ProcessEntireShardin', 'ookup/Lookup.cpp:757'),
    ('ProcessEntireShardin', 'ookup/Lookup.cpp:766'),
    ('ProcessEntireShardin', 'ookup/Lookup.cpp:792'),
    ('Clear', 'ork/Blacklist.cpp:72'),
    ('ConcatTranAndHash', 'otComputation.cpp:46'),
    ('ComputeRoot', 'otComputation.cpp:96'),
    ('FallbackTimerLaunch', 'reProcessing.cpp:284'),
    ('GetRecentTransaction', 'rver/Server.cpp:1050'),
    ('GetShardingStructure', 'rver/Server.cpp:1073'),
    ('GetNumTxnsTxEpoch', 'rver/Server.cpp:1100'),
    ('GetNumTxnsDSEpoch', 'rver/Server.cpp:1114'),
    ('IncreaseEpochNum', 'tor/Mediator.cpp:147'),
    ('CheckWhetherBlockIsL', 'tor/Mediator.cpp:176'),
    ('CommitStateDB', 'tractStorage.cpp:312'),
    ('InitTempState', 'tractStorage.cpp:364'),
    ('GetStateRootHash', 'untStoreTrie.tpp:102'),
    ('ClearBroadcastHashAs', 'work/P2PComm.cpp:359'),
    ('ProcessBroadCastMsg', 'work/P2PComm.cpp:397'),
    ('EventCallback', 'work/P2PComm.cpp:589'),
    ('SendBroadcastMessage', 'work/P2PComm.cpp:828')
)

if __name__ == '__main__':
    tags = []
    with open('ctags.txt') as f:
        ctags = f.readlines()
    for line in ctags:
        tag, rest = line.split('function', 1)
        tag = tag.strip()
        if len(tag.split()) > 2:
            continue
        lineno, path, code = rest.split(None, 2)
        if not lineno.isdigit():
            continue
        # tags.append((tag, path, int(lineno), code))
        tags.append((tag, path, int(lineno)))

    tags = tuple(tags)

    with open('tagindex.py', 'wb') as f:
        f.write('\n'.join([
            '# generated by ' + os.path.basename(__file__),
            'tags = ' + str(tags),
            'cache = {}'
        ]) + '\n')

    import recovery

    for d in data:
        recovery.recover(*d, tags=tags)
    with open('tagindex.py', 'wb') as f:
        f.write('\n'.join([
            '# generated by ' + os.path.basename(__file__),
            'tags = ' + str(tags),
            'cache = ' + str(recovery.cache)
        ]) + '\n')
