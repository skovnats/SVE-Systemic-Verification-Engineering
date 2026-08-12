% shasum -a 256 README.md 
52f94edd11fd7222f16cdf4c88917dbcef74f4e19e44731e1d6e953fe98f0e94  README.md

% shasum -a 256 timestamp.zip
0a64fce06680c52e03253ca26c4a99a8c3bcd5353b45848a045efc3353359799  timestamp.zip

% find analysis -type f -print0 | xargs -0 shasum -a 256 | shasum -a 256
b8317db70c428a5f437e5eb3f4246ac6e64d894fceda5db47027bd3ba22f2004  -


% hashdeep -r analysis
%%%% HASHDEEP-1.0
%%%% size,md5,sha256,filename
## Invoked from: /Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial
## $ hashdeep -r analysis
## 
6148,c016c55efe9894fb4fb64b287655390a,e185c81996c5853b5028ce8326a3c35687d24b072d5b0ef5f9a31b8775e6ae91,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/.DS_Store
588,00d36331bc6b73ad6289abf357243692,5752b4a86060cedf4ba3c67ca64144be35bb03ab9704d61147300fd137413de9,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/case_1/analysis_config.yaml
6148,1d57922e72091f87c23ec949eaed1ae4,dd594f4c1e3335e567c81fccecd1c39940c8201cbf0eb94cc5a6f38453b263ea,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/case_1/.DS_Store
84304,9e1f53bb9c55e0d7df98b36717aa4932,e4702216c99f24d48351504ec903720dd68652f1c2d54e38532d8465562e2043,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/case_1/data-for-analysis.csv
65366,e96bc6c7b09ea65a8894d6dc48a2f6da,b0cf30161c61794f38e4c6d32eddf60e0017ec75f45714bca34a36fb007bc08e,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/case_1/analysis.ipynb
128034,694a1a246cffd633b1c337cb2eabcba8,409e06e1d4150f1404fd0a01ac2bf038a91ca316760860daa00e8198ccf41286,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/case_1/calls-analysis-complete.csv
129508,bfd9e65d9405fd05edb269d564badea7,4b7c7bc95de7bfa6511d2551a761cc3e263c12675762bcb3157e5be633b34e0c,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/case_1/processing.ipynb
