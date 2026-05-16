UWE-4 Demodulation

GNU Radio + Python demodulation chain for decoding UWE-4 satellite FSK 9600 AX.25 IQ data into telemetry frames.

Overview

This project processes recorded IQ data from the UWE-4 satellite and extracts telemetry using a full digital signal processing chain implemented in GNU Radio and Python. The pipeline includes filtering, quadrature demodulation, clock recovery, NRZI decoding, descrambling, and HDLC frame extraction.

Observation Details
Observation ID: #14011420
Satellite: 43880 - UWE-4
Timeframes: UTC
Data Type: IQ recording (SDR capture)
IQ Source

The IQ recordings for this observation are available at:
[PE0SAT UWE-4 IQ Data](iq_14011420_435599000_57600.raw.zip	)

Processing Chain
IQ Data Input
Band filtering
Quadrature demodulation
Clock recovery (MM)
NRZI decoding
AX.25 / HDLC frame extraction
Telemetry frame output
Output

Recovered satellite telemetry frames ready for further decoding and analysis.
