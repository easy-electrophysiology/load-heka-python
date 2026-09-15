"""
------------------------------------------------------------------------------------------------------------------------------------------------------
 Trees_v2000
------------------------------------------------------------------------------------------------------------------------------------------------------

The v2000 file format (PatchMaster Next v1.6.0+) is identical to v1000 except for the
bundle header (see BundleHeaderV2000 in SharedTrees) and the TraceRecord, where the
following fields were widened from INT32 to INT64 to support very large / continuous
recordings:

    TrData            (INT32 -> INT64)
    TrDataPoints      (INT32 -> INT64)
    TrInterleaveSize  (INT32 -> INT64)
    TrInterleaveSkip  (INT32 -> INT64)

This shifts all subsequent offsets by +16 bytes, so TraceRecSize is 528 (was 512).
All other records (Group, Series, Sweep, Root and the Stim / Ampl / Solution / Marker /
Analysis trees) are unchanged and re-exported from Trees_v1000.
"""

from .Trees_v1000 import *  # noqa: F401,F403  re-export all unchanged records
from .SharedTrees import cstr, Description, get_data_kind, get_recording_mode


class TraceRecord(Description):
    def __init__(self, n=1):
        super(TraceRecord, self).__init__(n)

        self.description = [
            ("TrMark", "i"),  # (* INT32 *)
            ("TrLabel", "32s", cstr),  # (* String32Type *)
            ("TrTraceID", "i"),  # (* INT32 *)
            ("TrData", "q"),  # (* INT64 *)
            ("TrDataPoints", "q"),  # (* INT64 *)
            ("TrInternalSolution", "i"),  # (* INT32 *)
            ("TrAverageCount", "i"),  # (* INT32 *)
            ("TrLeakID", "i"),  # (* INT32 *)
            ("TrLeakTraces", "i"),  # (* INT32 *)
            ("TrDataKind", "h", get_data_kind),  # (* SET16 *)
            ("TrUseXStart", "?"),  # (* BOOLEAN *)
            ("TrTcKind", "b"),  # (* BYTE *)
            ("TrRecordingMode", "b", get_recording_mode),  # (* BYTE *)
            ("TrAmplIndex", "c"),  # (* CHAR *)
            ("TrDataFormat", "b"),  # (* BYTE *)
            ("TrDataAbscissa", "b"),  # (* BYTE *)
            ("TrDataScaler", "d"),  # (* LONGREAL *)
            ("TrTimeOffset", "d"),  # (* LONGREAL *)
            ("TrZeroData", "d"),  # (* LONGREAL *)
            ("TrYUnit", "8s", cstr),  # (* String8Type *)
            ("TrXInterval", "d"),  # (* LONGREAL *)
            ("TrXStart", "d"),  # (* LONGREAL *)
            ("TrXUnit", "8s", cstr),  # (* String8Type *)
            ("TrYRange", "d"),  # (* LONGREAL *)
            ("TrYOffset", "d"),  # (* LONGREAL *)
            ("TrBandwidth", "d"),  # (* LONGREAL *)
            ("TrPipetteResistance", "d"),  # (* LONGREAL *)
            ("TrCellPotential", "d"),  # (* LONGREAL *)
            ("TrSealResistance", "d"),  # (* LONGREAL *)
            ("TrCSlow", "d"),  # (* LONGREAL *)
            ("TrGSeries", "d"),  # (* LONGREAL *)
            ("TrRsValue", "d"),  # (* LONGREAL *)
            ("TrGLeak", "d"),  # (* LONGREAL *)
            ("TrMConductance", "d"),  # (* LONGREAL *)
            ("TrLinkDAChannel", "i"),  # (* INT32 *)
            ("TrValidYrange", "?"),  # (* BOOLEAN *)
            ("TrAdcMode", "b"),  # (* CHAR *)
            ("TrAdcChannel", "h"),  # (* INT16 *)
            ("TrYmin", "d"),  # (* LONGREAL *)
            ("TrYmax", "d"),  # (* LONGREAL *)
            ("TrSourceChannel", "i"),  # (* INT32 *)
            ("TrExternalSolution", "i"),  # (* INT32 *)
            ("TrCM", "d"),  # (* LONGREAL *)
            ("TrGM", "d"),  # (* LONGREAL *)
            ("TrPhase", "d"),  # (* LONGREAL *)
            ("TrDataCRC", "I"),  # (* CARD32 *)
            ("TrCRC", "I"),  # (* CARD32 *)
            ("TrGS", "d"),  # (* LONGREAL *)
            ("TrSelfChannel", "i"),  # (* INT32 *)
            ("TrInterleaveSize", "q"),  # (* INT64 *)
            ("TrInterleaveSkip", "q"),  # (* INT64 *)
            ("TrImageIndex", "i"),  # (* INT32 *)
            ("TrTrMarkers", "10d"),  # (* ARRAY[0..9] OF LONGREAL *)
            ("TrSECM_X", "d"),  # (* LONGREAL *)
            ("TrSECM_Y", "d"),  # (* LONGREAL *)
            ("TrSECM_Z", "d"),  # (* LONGREAL *)
            ("TrTrHolding", "d"),  # (* LONGREAL *)
            ("TrTcEnumerator", "i"),  # (* INT32 *)
            ("TrXTrace", "i"),  # (* INT32 *)
            ("TrIntSolValue", "d"),  # (* LONGREAL *)
            ("TrExtSolValue", "d"),  # (* LONGREAL *)
            ("TrIntSolName", "32s", cstr),  # (* String32Size *)
            ("TrExtSolName", "32s", cstr),  # (* String32Size *)
            ("TrDataPedestal", "d"),  # (* LONGREAL *)
        ]
        self.size = 528
