# Network Intrusion Detection System (NIDS) with Machine Learning

**Current version:** 0.4.0 (see [CHANGELOG.md](CHANGELOG.md))

A CLI intrusion detector which classifies network connections as normal or attack (based on the NSL-KDD data set). It gives you a probability score for any given connection being an attack and allows you to adjust the threshold for when an alert is generated.

## Problem

To be able to detect harmful intrusions, the network intrusion detection systems must be able to identify harmful connections by monitoring traffic features. The attacks comprise a big percentage of actual traffic in benchmark datasets, and when one incident is not detected (a false negative), it tends to be more expensive than a false alarm. The intended project sees the detection problem as one of binary classification and measures the results focusing on the recall as opposed only to accuracy.

## Dataset

**NSL-KDD**, an improved version of the KDD'99 benchmark with redundant records removed.

- Training set: 125,973 connections
- Test set: 22,544 connections (57% attacks, including attack types absent from training)
- 41 features per connection: duration, protocol, service, flag, byte counts, and connection-rate statistics
- Labels: `normal` or one of 38 attack types, converted to a binary target (0 = normal, 1 = attack)

Categorical features (`protocol_type`, `service`, `flag`) are one-hot encoded, giving 122 model inputs.

## Results

Evaluated on the held-out test set.

| Model | Attack precision | Attack recall | Attack F1 | Accuracy |
|---|---|---|---|---|
| Logistic Regression (baseline) | 0.917 | 0.624 | 0.743 | 0.754 |
| Random Forest | 0.967 | 0.610 | 0.748 | 0.766 |
| Random Forest (`class_weight="balanced"`) | 0.969 | 0.630 | 0.763 | 0.778 |

The class-weighted Random Forest is the saved model.

## Key Finding: Known vs. Novel Attacks

Recall depends heavily on whether the attack type appeared in training:

- **Attack types seen in training:** 76.8% recall
- **Novel attack types:** 22.7% recall

Flooding and scanning attacks (such as neptune, smurf, satan, portsweep, ipsweep, and nmap) are almost perfectly detected since the unique traffic patterns they exhibit are instantly recognizable. Conversely, stealthy, application-layer attacks (such as guess_passwd, snmpguess, mailbomb, and snmpgetattack) tend to go unnoticed because their connecting feature is similar to that of normal traffic. A few unusual types of attacks contain very few test samples, so their effectiveness cannot be relied upon.

## Project Structure
    nids-ml/
    ├── data/ # NSL-KDD files (not included)
    ├── models/ # saved model and feature columns
    ├── src/
    │ ├── preprocess.py # loading, labeling, encoding
    │ ├── train.py # training and evaluation
    │ ├── analyze.py # per-attack-type recall
    │ ├── predict.py # scoring and alert output
    │ └── cli.py # command-line interface
    ├── requirements.txt
    └── README.md


## Setup

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Download `KDDTrain+.txt` and `KDDTest+.txt` from the NSL-KDD dataset (Any mirror) and place them in `data/`.

## Usage

Train and evaluate the models:

```bash
python -m src.train
```

Score a file and write alerts to CSV:

```bash
python -m src.cli predict --input data/KDDTest+.txt --output alerts.csv
```

A lower threshold produces more alerts, catching more attacks at the cost of more false alarms:

```bash
python -m src.cli predict --input data/KDDTest+.txt --threshold 0.3 --output alerts_low.csv
```

On the test set, the default threshold (0.5) flags 8,380 connections, and 0.3 flags 9,530.

Show metrics on a labeled test file:

```bash
python -m src.cli report
```

## Limitations

- **Year of the dataset:** Conducted in 1999, the NSL-KDD dataset will help build a model but will not simulate actual networks in use, nor will it provide any information about encrypted traffic.
- **Feature level:** This model is based on connection features that collect statistics but do not analyze the actual packet contents.
- **Novel attacks:** Moreover, detection of attacks that were not included in the training set will have a low recall (22.7%). Therefore, in practice, systems will have to combine this model with alternatives.
- **Labeled input:** Currently, in NSL-KDD, the input command uses the label column. However, to receive output from non-labeled real-time data, a new loader will have to be implemented.

## Future Work

- Accept unlabeled input for real-time scoring
- Test on CIC-IDS2017 for more modern traffic
- Build a Streamlit dashboard for alert review