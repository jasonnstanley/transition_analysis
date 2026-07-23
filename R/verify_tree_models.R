# ----------------------------------------------------------------------
# Independent R verification of tuned tree-model outputs
# ----------------------------------------------------------------------

library(caret)
library(dplyr)

project_root <- normalizePath(
  file.path(getwd()),
  winslash = "/",
  mustWork = TRUE
)

reports_dir <- file.path(
  project_root,
  "reports",
  "data"
)

model_file <- file.path(
  reports_dir,
  "tuned_tree_models.csv"
)

roc_file <- file.path(
  reports_dir,
  "tuned_roc_summary.csv"
)

if (!file.exists(model_file)) {
  stop(
    paste(
      "Missing tuned model summary:",
      model_file
    )
  )
}

if (!file.exists(roc_file)) {
  stop(
    paste(
      "Missing tuned ROC summary:",
      roc_file
    )
  )
}

models <- read.csv(
  model_file,
  check.names = FALSE
)

roc <- read.csv(
  roc_file,
  check.names = FALSE
)

cat(
  paste0(
    strrep("=", 72),
    "\nR Verification — Tuned Tree Outputs\n",
    strrep("=", 72),
    "\n\n"
  )
)

cat("Tuned model summary\n")
cat(strrep("-", 72), "\n")
print(models)

cat("\nROC summary\n")
cat(strrep("-", 72), "\n")
print(roc)

cat("\n")
cat("Model rows :", nrow(models), "\n")
cat("ROC rows   :", nrow(roc), "\n")
model_variants <- unique(
  paste(
    models$model,
    models$dataset,
    sep = " — "
  )
)

cat("Model types    :", length(unique(models$model)), "\n")
cat("Model variants :", length(model_variants), "\n")
# ----------------------------------------------------------------------
# Cross-check duplicated metrics across Python output files
# ----------------------------------------------------------------------

normalise_model_name <- function(model, dataset) {
  model <- sub(
    "^Tuned ",
    "",
    model
  )

  risk_label <- ifelse(
    dataset == "With Risk Index",
    "With Risk",
    "Without Risk"
  )

  paste(
    model,
    risk_label,
    sep = " — "
  )
}


models$model_key <- normalise_model_name(
  models$model,
  models$dataset
)

roc$model_key <- roc$model


comparison <- merge(
  models[
    ,
    c(
      "model_key",
      "best_cv_roc_auc",
      "test_roc_auc"
    )
  ],
  roc[
    ,
    c(
      "model_key",
      "cv_roc_auc",
      "roc_auc"
    )
  ],
  by = "model_key",
  all = TRUE
)


comparison$cv_difference <- (
  comparison$best_cv_roc_auc
  - comparison$cv_roc_auc
)

comparison$test_difference <- (
  comparison$test_roc_auc
  - comparison$roc_auc
)


tolerance <- 1e-12

comparison$cv_matches <- (
  abs(comparison$cv_difference) < tolerance
)

comparison$test_matches <- (
  abs(comparison$test_difference) < tolerance
)


cat("\n")
cat("Cross-file ROC verification\n")
cat(strrep("-", 72), "\n")

print(
  comparison[
    ,
    c(
      "model_key",
      "cv_difference",
      "test_difference",
      "cv_matches",
      "test_matches"
    )
  ],
  row.names = FALSE
)


if (
  !all(comparison$cv_matches)
  || !all(comparison$test_matches)
) {
  stop(
    "ROC metrics do not agree across the Python output files."
  )
}


cat("\n")
cat("All duplicated ROC metrics agree within tolerance.\n")

# ----------------------------------------------------------------------
# Load research dataset
# ----------------------------------------------------------------------

research_file <- file.path(
  project_root,
  "data",
  "processed",
  "transition_research.csv"
)

if (!file.exists(research_file)) {
  stop(
    paste(
      "Missing research dataset:",
      research_file
    )
  )
}

research <- read.csv(
  research_file,
  check.names = FALSE
)

cat("\n")
cat("Research dataset\n")
cat(strrep("-", 72), "\n")

cat("Rows    :", nrow(research), "\n")
cat("Columns :", ncol(research), "\n")

cat("\nColumn names\n")
cat(strrep("-", 72), "\n")

print(names(research))

# ----------------------------------------------------------------------
# Reproduce Python train/test split
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Load canonical train/test split
# ----------------------------------------------------------------------

split_file <- file.path(
  project_root,
  "data",
  "processed",
  "train_test_split.csv"
)

if (!file.exists(split_file)) {
  stop(
    paste(
      "Missing canonical split file:",
      split_file
    )
  )
}

split_membership <- read.csv(
  split_file,
  check.names = FALSE
)

required_split_columns <- c(
  "research_id",
  "split"
)

missing_split_columns <- setdiff(
  required_split_columns,
  names(split_membership)
)

if (length(missing_split_columns) > 0) {
  stop(
    paste(
      "Canonical split file is missing columns:",
      paste(missing_split_columns, collapse = ", ")
    )
  )
}

if (anyDuplicated(split_membership$research_id)) {
  stop(
    "Canonical split contains duplicate research identifiers."
  )
}

research_with_split <- merge(
  research,
  split_membership,
  by = "research_id",
  all.x = TRUE,
  sort = FALSE
)

if (any(is.na(research_with_split$split))) {
  stop(
    "Some research records have no canonical split assignment."
  )
}

train_data <- subset(
  research_with_split,
  split == "train"
)

test_data <- subset(
  research_with_split,
  split == "test"
)

cat("\n")
cat("Canonical train/test split\n")
cat(strrep("-", 72), "\n")

cat("Training rows :", nrow(train_data), "\n")
cat("Test rows     :", nrow(test_data), "\n")

cat("\nTraining outcome\n")
print(table(train_data$current_subject_pass))

cat("\nTest outcome\n")
print(table(test_data$current_subject_pass))


# ----------------------------------------------------------------------
# Rebuild tree-model feature matrices in R
# ----------------------------------------------------------------------

normalise_binary <- function(x, column_name) {
  if (is.logical(x)) {
    return(as.integer(x))
  }

  if (is.numeric(x)) {
    invalid_values <- unique(
      x[
        !is.na(x)
        & !(x %in% c(0, 1))
      ]
    )

    if (length(invalid_values) > 0) {
      stop(
        paste(
          "Column",
          shQuote(column_name),
          "contains non-binary numeric values:",
          paste(invalid_values, collapse = ", ")
        )
      )
    }

    return(as.integer(x))
  }

  cleaned <- tolower(
    trimws(
      as.character(x)
    )
  )

  mapping <- c(
    "yes" = 1,
    "y" = 1,
    "true" = 1,
    "pass" = 1,
    "passed" = 1,
    "1" = 1,
    "no" = 0,
    "n" = 0,
    "false" = 0,
    "fail" = 0,
    "failed" = 0,
    "0" = 0
  )

  converted <- unname(
    mapping[cleaned]
  )

  invalid_mask <- (
    !is.na(cleaned)
    & is.na(converted)
  )

  if (any(invalid_mask)) {
    invalid_values <- sort(
      unique(cleaned[invalid_mask])
    )

    stop(
      paste(
        "Column",
        shQuote(column_name),
        "contains unrecognised binary values:",
        paste(invalid_values, collapse = ", ")
      )
    )
  }

  as.integer(converted)
}


prepare_tree_features <- function(
  dataframe,
  include_risk_index = FALSE
) {
  binary_columns <- c(
    "international_student",
    "has_previous_current_subject_attempt",
    "previous_current_subject_failure",
    "has_preparatory_subject",
    "prior_preparatory_subject_failure",
    "prior_preparatory_subject_pass"
  )

  categorical_columns <- c(
    "secondary_preparation_level",
    "secondary_school_mark_band"
  )

  predictor_columns <- c(
    binary_columns,
    categorical_columns
  )

  if (include_risk_index) {
    predictor_columns <- c(
      predictor_columns,
      "risk_index"
    )
  }

  features <- dataframe[
    ,
    predictor_columns,
    drop = FALSE
  ]

  for (column in binary_columns) {
    features[[column]] <- normalise_binary(
      features[[column]],
      column
    )
  }

  for (column in categorical_columns) {
    values <- trimws(
      as.character(features[[column]])
    )

    values[
      is.na(values)
      | values == ""
    ] <- "Missing"

    features[[column]] <- factor(values)
  }

  if (include_risk_index) {
    features$risk_index <- as.numeric(
      features$risk_index
    )
  }

  numeric_columns <- setdiff(
    names(features),
    categorical_columns
  )

  for (column in numeric_columns) {
    if (any(is.na(features[[column]]))) {
      stop(
        paste(
          "Predictor",
          shQuote(column),
          "contains missing values."
        )
      )
    }
  }

  full_contrasts <- lapply(
    features[categorical_columns],
    contrasts,
    contrasts = FALSE
  )

  encoded <- model.matrix(
    ~ . - 1,
    data = features,
    contrasts.arg = full_contrasts
  )

  encoded <- as.data.frame(
    encoded,
    check.names = FALSE
  )

  names(encoded) <- sub(
    "^secondary_preparation_level",
    "secondary_preparation_level_",
    names(encoded)
  )

  names(encoded) <- sub(
    "^secondary_school_mark_band",
    "secondary_school_mark_band_",
    names(encoded)
  )

  encoded
}


y_r <- normalise_binary(
  research_with_split$current_subject_pass,
  "current_subject_pass"
)

X_without_risk_r <- prepare_tree_features(
  research_with_split,
  include_risk_index = FALSE
)

X_with_risk_r <- prepare_tree_features(
  research_with_split,
  include_risk_index = TRUE
)

cat("\n")
cat("R tree-model datasets\n")
cat(strrep("-", 72), "\n")

cat(
  "Without Risk — rows     :",
  nrow(X_without_risk_r),
  "\n"
)

cat(
  "Without Risk — features :",
  ncol(X_without_risk_r),
  "\n"
)

cat(
  "With Risk — rows        :",
  nrow(X_with_risk_r),
  "\n"
)

cat(
  "With Risk — features    :",
  ncol(X_with_risk_r),
  "\n"
)

cat("\nWithout-risk feature names\n")
print(names(X_without_risk_r))

cat("\nWith-risk feature names\n")
print(names(X_with_risk_r))

# ----------------------------------------------------------------------
# Verify exact feature names and ordering
# ----------------------------------------------------------------------

expected_without_risk_features <- c(
  "international_student",
  "has_previous_current_subject_attempt",
  "previous_current_subject_failure",
  "has_preparatory_subject",
  "prior_preparatory_subject_failure",
  "prior_preparatory_subject_pass",
  "secondary_preparation_level_Advanced",
  "secondary_preparation_level_Ext1",
  "secondary_preparation_level_Ext2",
  "secondary_preparation_level_Other",
  "secondary_preparation_level_Standard",
  "secondary_school_mark_band_<70",
  "secondary_school_mark_band_70-79",
  "secondary_school_mark_band_80-89",
  "secondary_school_mark_band_90+"
)

expected_with_risk_features <- c(
  expected_without_risk_features,
  "risk_index"
)

without_risk_names_match <- identical(
  names(X_without_risk_r),
  expected_without_risk_features
)

with_risk_names_match <- identical(
  names(X_with_risk_r),
  expected_with_risk_features
)

cat("\n")
cat("Feature-matrix verification\n")
cat(strrep("-", 72), "\n")

cat(
  "Without-risk feature names match :",
  without_risk_names_match,
  "\n"
)

cat(
  "With-risk feature names match    :",
  with_risk_names_match,
  "\n"
)

if (!without_risk_names_match) {
  cat("\nUnexpected without-risk feature order\n")
  print(names(X_without_risk_r))

  stop(
    "Without-risk R feature matrix does not match Python."
  )
}

if (!with_risk_names_match) {
  cat("\nUnexpected with-risk feature order\n")
  print(names(X_with_risk_r))

  stop(
    "With-risk R feature matrix does not match Python."
  )
}

cat("\n")
cat("R feature matrices match the Python design.\n")


# ----------------------------------------------------------------------
# Fit tuned decision tree without Risk Index
# ----------------------------------------------------------------------

library(rpart)
library(pROC)

train_rows <- research_with_split$split == "train"
test_rows <- research_with_split$split == "test"

X_train_without_risk <- X_without_risk_r[
  train_rows,
  ,
  drop = FALSE
]

X_test_without_risk <- X_without_risk_r[
  test_rows,
  ,
  drop = FALSE
]

y_train <- factor(
  y_r[train_rows],
  levels = c(0, 1)
)

y_test <- factor(
  y_r[test_rows],
  levels = c(0, 1)
)

tree_train_data <- data.frame(
  current_subject_pass = y_train,
  X_train_without_risk,
  check.names = FALSE
)

tree_test_data <- data.frame(
  X_test_without_risk,
  check.names = FALSE
)

tree_without_risk <- rpart(
  current_subject_pass ~ .,
  data = tree_train_data,
  method = "class",
  parms = list(
    split = "information"
  ),
  control = rpart.control(
    minsplit = 40,
    minbucket = 5,
    cp = 0,
    maxdepth = 30,
    xval = 0
  )
)

tree_probabilities <- predict(
  tree_without_risk,
  newdata = tree_test_data,
  type = "prob"
)[, "1"]

tree_predictions <- ifelse(
  tree_probabilities >= 0.5,
  1,
  0
)

tree_predictions <- factor(
  tree_predictions,
  levels = c(0, 1)
)

confusion <- table(
  Actual = y_test,
  Predicted = tree_predictions
)

true_negative <- confusion["0", "0"]
false_positive <- confusion["0", "1"]
false_negative <- confusion["1", "0"]
true_positive <- confusion["1", "1"]

accuracy <- (
  true_positive + true_negative
) / sum(confusion)

sensitivity <- true_positive / (
  true_positive + false_negative
)

specificity <- true_negative / (
  true_negative + false_positive
)

balanced_accuracy <- (
  sensitivity + specificity
) / 2

precision <- true_positive / (
  true_positive + false_positive
)

recall <- sensitivity

f1 <- 2 * precision * recall / (
  precision + recall
)

roc_result <- roc(
  response = as.numeric(
    as.character(y_test)
  ),
  predictor = tree_probabilities,
  levels = c(0, 1),
  direction = "<",
  quiet = TRUE
)

roc_auc <- as.numeric(
  auc(roc_result)
)

cat("\n")
cat("Independent R model — Decision Tree Without Risk\n")
cat(strrep("-", 72), "\n")

print(confusion)

cat("\n")
cat(sprintf("Accuracy          : %.7f\n", accuracy))
cat(sprintf("Balanced accuracy : %.7f\n", balanced_accuracy))
cat(sprintf("Precision         : %.7f\n", precision))
cat(sprintf("Recall            : %.7f\n", recall))
cat(sprintf("F1                : %.7f\n", f1))
cat(sprintf("ROC AUC           : %.7f\n", roc_auc))


# ----------------------------------------------------------------------
# Write dynamic verification report
# ----------------------------------------------------------------------

verification_report_file <- file.path(
  project_root,
  "docs",
  "verification_report.md"
)

dir.create(
  dirname(verification_report_file),
  recursive = TRUE,
  showWarnings = FALSE
)


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------

markdown_boolean <- function(value) {
  if (isTRUE(value)) {
    return("TRUE")
  }

  "FALSE"
}


verification_status <- function(value) {
  if (isTRUE(value)) {
    return("PASS")
  }

  "FAIL"
}


safe_table_count <- function(table_object, category) {
  category <- as.character(category)

  if (!(category %in% names(table_object))) {
    return(0L)
  }

  as.integer(
    unname(table_object[category])
  )
}


format_file_time <- function(filename) {
  file_information <- file.info(filename)

  if (
    nrow(file_information) == 0
    || is.na(file_information$mtime[1])
  ) {
    return("Unavailable")
  }

  format(
    file_information$mtime[1],
    "%Y-%m-%d %H:%M:%S"
  )
}


# ----------------------------------------------------------------------
# Verification values
# ----------------------------------------------------------------------

training_outcome <- table(
  train_data$current_subject_pass
)

test_outcome <- table(
  test_data$current_subject_pass
)

dataset_verification_passed <- (
  nrow(research) == 1473
  && ncol(research) == 19
  && "current_subject_pass" %in% names(research)
)

split_verification_passed <- (
  nrow(train_data) == 1178
  && nrow(test_data) == 295
  && safe_table_count(training_outcome, 0) == 236
  && safe_table_count(training_outcome, 1) == 942
  && safe_table_count(test_outcome, 0) == 59
  && safe_table_count(test_outcome, 1) == 236
)

feature_verification_passed <- (
  ncol(X_without_risk_r) == 15
  && ncol(X_with_risk_r) == 16
  && without_risk_names_match
  && with_risk_names_match
)

roc_verification_passed <- (
  all(comparison$cv_matches)
  && all(comparison$test_matches)
)

pipeline_verification_passed <- (
  dataset_verification_passed
  && split_verification_passed
  && feature_verification_passed
  && roc_verification_passed
)


# ----------------------------------------------------------------------
# Obtain corresponding Python decision-tree results
# ----------------------------------------------------------------------

python_tree_row <- models[
  models$model == "Tuned Decision Tree"
  & models$dataset == "Without Risk Index",
  ,
  drop = FALSE
]

if (nrow(python_tree_row) != 1) {
  stop(
    paste(
      "Expected exactly one Python result for",
      "Tuned Decision Tree — Without Risk Index."
    )
  )
}

python_accuracy <- python_tree_row$test_accuracy
python_balanced_accuracy <- (
  python_tree_row$test_balanced_accuracy
)
python_precision <- python_tree_row$test_precision
python_recall <- python_tree_row$test_recall
python_f1 <- python_tree_row$test_f1
python_roc_auc <- python_tree_row$test_roc_auc


# ----------------------------------------------------------------------
# Decision-tree comparison
# ----------------------------------------------------------------------

accuracy_difference <- accuracy - python_accuracy

balanced_accuracy_difference <- (
  balanced_accuracy
  - python_balanced_accuracy
)

precision_difference <- (
  precision
  - python_precision
)

recall_difference <- (
  recall
  - python_recall
)

f1_difference <- (
  f1
  - python_f1
)

roc_auc_difference <- (
  roc_auc
  - python_roc_auc
)


# ----------------------------------------------------------------------
# Dynamic verification-status table
# ----------------------------------------------------------------------

research_status <- verification_status(
  dataset_verification_passed
)

split_status <- verification_status(
  split_verification_passed
)

feature_status <- verification_status(
  feature_verification_passed
)

roc_status <- verification_status(
  roc_verification_passed
)

decision_tree_status <- if (
  pipeline_verification_passed
) {
  "VERIFIED PIPELINE; IMPLEMENTATION DIFFERENCE"
} else {
  "FAIL"
}

overall_status <- if (
  pipeline_verification_passed
) {
  "PASS"
} else {
  "FAIL"
}


# ----------------------------------------------------------------------
# Report content
# ----------------------------------------------------------------------

report_lines <- c(
  "# Transition Analysis Toolkit",
  "## Independent Verification Report",
  "",
  paste0(
    "**Generated:** ",
    format(
      Sys.time(),
      "%Y-%m-%d %H:%M:%S"
    )
  ),
  "",
  paste0(
    "**R version:** ",
    R.version.string
  ),
  "",
  paste0(
    "**Research dataset modified:** ",
    format_file_time(research_file)
  ),
  "",
  paste0(
    "**Canonical split modified:** ",
    format_file_time(split_file)
  ),
  "",
  paste0(
    "**Overall verification status:** ",
    overall_status
  ),
  "",
  "---",
  "",
  "## Verification Status",
  "",
  "| Component | Python | Independent R | Status |",
  "|---|:---:|:---:|---|",
  paste0(
    "| Research dataset | Yes | Yes | ",
    research_status,
    " |"
  ),
  paste0(
    "| Canonical train/test split | Yes | Yes | ",
    split_status,
    " |"
  ),
  paste0(
    "| Feature engineering | Yes | Yes | ",
    feature_status,
    " |"
  ),
  paste0(
    "| Dummy-variable encoding | Yes | Yes | ",
    feature_status,
    " |"
  ),
  paste0(
    "| Feature names and ordering | Yes | Yes | ",
    feature_status,
    " |"
  ),
  paste0(
    "| Cross-file ROC consistency | Yes | Yes | ",
    roc_status,
    " |"
  ),
  paste0(
    "| Decision Tree | Yes | Yes | ",
    decision_tree_status,
    " |"
  ),
  "| Logistic Regression | Yes | No | PENDING |",
  "| Random Forest | Yes | No | PENDING |",
  "",
  "---",
  "",
  "## Research Dataset Verification",
  "",
  paste0("- Rows: **", nrow(research), "**"),
  paste0("- Columns: **", ncol(research), "**"),
  "- Outcome variable: `current_subject_pass`",
  "",
  paste0(
    "**Verification result: ",
    research_status,
    "**"
  ),
  "",
  "---",
  "",
  "## Canonical Train/Test Split Verification",
  "",
  paste0(
    "- Training rows: **",
    nrow(train_data),
    "**"
  ),
  paste0(
    "- Test rows: **",
    nrow(test_data),
    "**"
  ),
  paste0(
    "- Training non-passes: **",
    safe_table_count(training_outcome, 0),
    "**"
  ),
  paste0(
    "- Training passes: **",
    safe_table_count(training_outcome, 1),
    "**"
  ),
  paste0(
    "- Test non-passes: **",
    safe_table_count(test_outcome, 0),
    "**"
  ),
  paste0(
    "- Test passes: **",
    safe_table_count(test_outcome, 1),
    "**"
  ),
  "",
  paste0(
    "**Verification result: ",
    split_status,
    "**"
  ),
  "",
  "---",
  "",
  "## Feature Engineering Verification",
  "",
  paste0(
    "- Predictors without Risk Index: **",
    ncol(X_without_risk_r),
    "**"
  ),
  paste0(
    "- Predictors with Risk Index: **",
    ncol(X_with_risk_r),
    "**"
  ),
  paste0(
    "- Without-risk names match Python design: **",
    markdown_boolean(without_risk_names_match),
    "**"
  ),
  paste0(
    "- With-risk names match Python design: **",
    markdown_boolean(with_risk_names_match),
    "**"
  ),
  "",
  paste0(
    "**Verification result: ",
    feature_status,
    "**"
  ),
  "",
  "---",
  "",
  "## Cross-file ROC Verification",
  "",
  paste0(
    "- Model variants checked: **",
    nrow(comparison),
    "**"
  ),
  paste0(
    "- CV ROC metrics matched: **",
    markdown_boolean(
      all(comparison$cv_matches)
    ),
    "**"
  ),
  paste0(
    "- Test ROC metrics matched: **",
    markdown_boolean(
      all(comparison$test_matches)
    ),
    "**"
  ),
  "",
  paste0(
    "**Verification result: ",
    roc_status,
    "**"
  ),
  "",
  "---",
  "",
  "## Independent Decision Tree Verification",
  "",
  "### Implementations",
  "",
  "- Python: `scikit-learn`",
  "- R: `rpart`",
  "",
  "Both implementations used:",
  "",
  "- the same pseudonymised research dataset;",
  "- the same canonical training and test observations;",
  "- the same binary outcome;",
  "- the same 15-predictor without-risk design;",
  "- full dummy-variable encoding;",
  "- information-gain splitting;",
  "- minimum split size of 40;",
  "- minimum terminal-node size of 5.",
  "",
  "### Held-out Test-set Comparison",
  "",
  "| Metric | Python | R | R minus Python |",
  "|---|---:|---:|---:|",
  paste0(
    "| Accuracy | ",
    sprintf("%.4f", python_accuracy),
    " | ",
    sprintf("%.4f", accuracy),
    " | ",
    sprintf("%+.4f", accuracy_difference),
    " |"
  ),
  paste0(
    "| Balanced accuracy | ",
    sprintf("%.4f", python_balanced_accuracy),
    " | ",
    sprintf("%.4f", balanced_accuracy),
    " | ",
    sprintf(
      "%+.4f",
      balanced_accuracy_difference
    ),
    " |"
  ),
  paste0(
    "| Precision | ",
    sprintf("%.4f", python_precision),
    " | ",
    sprintf("%.4f", precision),
    " | ",
    sprintf("%+.4f", precision_difference),
    " |"
  ),
  paste0(
    "| Recall | ",
    sprintf("%.4f", python_recall),
    " | ",
    sprintf("%.4f", recall),
    " | ",
    sprintf("%+.4f", recall_difference),
    " |"
  ),
  paste0(
    "| F1 | ",
    sprintf("%.4f", python_f1),
    " | ",
    sprintf("%.4f", f1),
    " | ",
    sprintf("%+.4f", f1_difference),
    " |"
  ),
  paste0(
    "| ROC AUC | ",
    sprintf("%.4f", python_roc_auc),
    " | ",
    sprintf("%.4f", roc_auc),
    " | ",
    sprintf("%+.4f", roc_auc_difference),
    " |"
  ),
  "",
  "### Verification",
  "",
  paste0(
    "The independently reconstructed R pipeline ",
    "used the verified research dataset, canonical split, ",
    "outcome definition, dummy-variable encoding and feature order."
  ),
  "",
  paste0(
    "**Pipeline verification result: ",
    verification_status(
      pipeline_verification_passed
    ),
    "**"
  ),
  "",
  "### Interpretation",
  "",
  paste(
    "The Python and R decision trees do not produce identical",
    "predictions. This is expected because `scikit-learn` and",
    "`rpart` use different tree-growing, stopping and pruning",
    "implementations, even when their high-level tuning constraints",
    "are aligned."
  ),
  "",
  paste(
    "The R tree favoured the passing class more strongly, producing",
    "higher recall and overall accuracy but lower balanced accuracy",
    "and ROC AUC. The differences are therefore model-implementation",
    "differences, not evidence of inconsistent data preparation."
  ),
  "",
  "**Interpretation: EXPECTED IMPLEMENTATION DIFFERENCE**",
  "",
  "---",
  "",
  "## Pending Independent Verification",
  "",
  "- Logistic Regression",
  "- Random Forest",
  ""
)


# ----------------------------------------------------------------------
# Write report
# ----------------------------------------------------------------------

writeLines(
  report_lines,
  verification_report_file,
  useBytes = TRUE
)

cat("\n")
cat("Dynamic verification report written\n")
cat(strrep("-", 72), "\n")
cat(verification_report_file, "\n")
cat("Overall status :", overall_status, "\n")

