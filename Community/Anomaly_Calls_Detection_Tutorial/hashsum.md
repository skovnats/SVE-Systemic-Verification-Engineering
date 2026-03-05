% shasum -a 256 README.md 
52f94edd11fd7222f16cdf4c88917dbcef74f4e19e44731e1d6e953fe98f0e94  README.md

% find analysis -type f -print0 | xargs -0 shasum -a 256 | shasum -a 256
61fcca29db151eaee76675da381ea547ad53780f234abe7d5c58de68541212c1  -


% hashdeep -r analysis
%%%% HASHDEEP-1.0
%%%% size,md5,sha256,filename
## Invoked from: /Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial
## $ hashdeep -r analysis
## 
6148,f413adeea3c983d48267245296204888,eefac3b8898dedf8f7ea858aeb5adefac9bc71e287281a452c1d01ff5324e0a3,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/.DS_Store
588,00d36331bc6b73ad6289abf357243692,5752b4a86060cedf4ba3c67ca64144be35bb03ab9704d61147300fd137413de9,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/case_1/analysis_config.yaml
6148,1d57922e72091f87c23ec949eaed1ae4,dd594f4c1e3335e567c81fccecd1c39940c8201cbf0eb94cc5a6f38453b263ea,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/case_1/.DS_Store
65366,e96bc6c7b09ea65a8894d6dc48a2f6da,b0cf30161c61794f38e4c6d32eddf60e0017ec75f45714bca34a36fb007bc08e,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/case_1/analysis.ipynb
128034,694a1a246cffd633b1c337cb2eabcba8,409e06e1d4150f1404fd0a01ac2bf038a91ca316760860daa00e8198ccf41286,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/case_1/calls-analysis-complete.csv
84304,9e1f53bb9c55e0d7df98b36717aa4932,e4702216c99f24d48351504ec903720dd68652f1c2d54e38532d8465562e2043,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/case_1/data-for-analysis.csv
129508,bfd9e65d9405fd05edb269d564badea7,4b7c7bc95de7bfa6511d2551a761cc3e263c12675762bcb3157e5be633b34e0c,/Users/artiom/Desktop/SVE-Systemic-Verification-Engineering/Community/Anomaly_Calls_Detection_Tutorial/analysis/case_1/processing.ipynb