# =============================================================================
# Independent Logistic Regression Verification
# Transition Analysis Toolkit
# =============================================================================

options(stringsAsFactors = FALSE)

cat("\n")
cat("Independent Logistic Regression Verification\n")
cat(paste(rep("=", 72), collapse = ""), "\n", sep = "")
cat("\n")

# -----------------------------------------------------------------------------
# Project paths
# -----------------------------------------------------------------------------

project_root <- normalizePath(".", winslash = "/", mustWork = TRUE)

research_data_path <- file.path(
  project_root,
  "data",
  "processed",
  "transition_research.csv"
)

canonical_split_path <- file.path(
  project_root,
  "data",
  "processed",
  "train_test_split.csv"
)

output_dir <- file.path(
  project_root,
  "reports"
)

log_dir <- file.path(
  project_root,
  "logs"
)

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(log_dir, recursive = TRUE, showWarnings = FALSE)

# -----------------------------------------------------------------------------
# Confirm required files
# -----------------------------------------------------------------------------

required_files <- c(
  research_data_path,
  canonical_split_path
)

missing_files <- required_files[!file.exists(required_files)]

if (length(missing_files) > 0) {
  stop(
    paste(
      "Required file(s) not found:",
      paste(missing_files, collapse = "\n")
    )
  )
}

cat("Required files found.\n")
cat("\n")

# -----------------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------------

research_data <- read.csv(
  research_data_path,
  check.names = FALSE,
  na.strings = c("", "NA")
)

canonical_split <- read.csv(
  canonical_split_path,
  check.names = FALSE,
  na.strings = c("", "NA")
)

cat("Research rows:       ", nrow(research_data), "\n", sep = "")
cat("Research columns:    ", ncol(research_data), "\n", sep = "")
cat("Split rows:          ", nrow(canonical_split), "\n", sep = "")
cat("\n")

# -----------------------------------------------------------------------------
# Initial structural checks
# -----------------------------------------------------------------------------

required_research_columns <- c(
  "research_id",
  "current_subject_pass"
)

missing_research_columns <- setdiff(
  required_research_columns,
  names(research_data)
)

if (length(missing_research_columns) > 0) {
  stop(
    paste(
      "Missing research column(s):",
      paste(missing_research_columns, collapse = ", ")
    )
  )
}

if (!"research_id" %in% names(canonical_split)) {
  stop("canonical_split.csv does not contain research_id.")
}

cat("Initial structural checks: PASS\n")
cat("\n")

# -----------------------------------------------------------------------------
# Verify canonical split structure
# -----------------------------------------------------------------------------

required_split_columns <- c(
  "research_id",
  "split"
)

missing_split_columns <- setdiff(
  required_split_columns,
  names(canonical_split)
)

if (length(missing_split_columns) > 0) {
  stop(
    paste(
      "Missing canonical split column(s):",
      paste(missing_split_columns, collapse = ", ")
    )
  )
}

duplicate_research_ids <- canonical_split$research_id[
  duplicated(canonical_split$research_id)
]

if (length(duplicate_research_ids) > 0) {
  stop("Duplicate research_id values found in canonical split.")
}

unknown_split_ids <- setdiff(
  canonical_split$research_id,
  research_data$research_id
)

if (length(unknown_split_ids) > 0) {
  stop("Canonical split contains research_id values not found in research data.")
}

missing_split_ids <- setdiff(
  research_data$research_id,
  canonical_split$research_id
)

if (length(missing_split_ids) > 0) {
  stop("Some research observations are missing from the canonical split.")
}

split_values <- sort(unique(canonical_split$split))

expected_split_values <- c(
  "test",
  "train"
)

if (!identical(split_values, expected_split_values)) {
  stop(
    paste(
      "Unexpected canonical split labels:",
      paste(split_values, collapse = ", ")
    )
  )
}

# -----------------------------------------------------------------------------
# Join split assignment to research data
# -----------------------------------------------------------------------------

analysis_data <- merge(
  research_data,
  canonical_split,
  by = "research_id",
  all.x = TRUE,
  sort = FALSE
)

if (any(is.na(analysis_data$split))) {
  stop("Split assignment is missing after joining research data.")
}

train_data <- analysis_data[
  analysis_data$split == "train",
  ,
  drop = FALSE
]

test_data <- analysis_data[
  analysis_data$split == "test",
  ,
  drop = FALSE
]

cat("Canonical split verification\n")
cat(paste(rep("-", 72), collapse = ""), "\n", sep = "")
cat("Training rows:       ", nrow(train_data), "\n", sep = "")
cat("Test rows:           ", nrow(test_data), "\n", sep = "")
cat("\n")

cat("Training outcome counts\n")
print(table(train_data$current_subject_pass))
cat("\n")

cat("Test outcome counts\n")
print(table(test_data$current_subject_pass))
cat("\n")

cat("Canonical split verification: PASS\n")
cat("\n")
# -----------------------------------------------------------------------------
# Rebuild logistic-regression feature matrices
# -----------------------------------------------------------------------------

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


prepare_logistic_features <- function(
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
  analysis_data$current_subject_pass,
  "current_subject_pass"
)

X_without_risk_r <- prepare_logistic_features(
  analysis_data,
  include_risk_index = FALSE
)

X_with_risk_r <- prepare_logistic_features(
  analysis_data,
  include_risk_index = TRUE
)


# -----------------------------------------------------------------------------
# Verify feature names and ordering
# -----------------------------------------------------------------------------

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

if (!identical(
  names(X_without_risk_r),
  expected_without_risk_features
)) {
  stop(
    "Without-risk feature names do not match the verified Python design."
  )
}

if (!identical(
  names(X_with_risk_r),
  expected_with_risk_features
)) {
  stop(
    "With-risk feature names do not match the verified Python design."
  )
}


# -----------------------------------------------------------------------------
# Extract canonical training and test matrices
# -----------------------------------------------------------------------------

train_rows <- analysis_data$split == "train"
test_rows <- analysis_data$split == "test"

x_train_without_risk <- X_without_risk_r[
  train_rows,
  ,
  drop = FALSE
]

x_test_without_risk <- X_without_risk_r[
  test_rows,
  ,
  drop = FALSE
]

x_train_with_risk <- X_with_risk_r[
  train_rows,
  ,
  drop = FALSE
]

x_test_with_risk <- X_with_risk_r[
  test_rows,
  ,
  drop = FALSE
]

y_train <- y_r[train_rows]
y_test <- y_r[test_rows]
logistic_train <- data.frame(
  current_subject_pass = factor(
    y_train,
    levels = c(0, 1)
  ),
  x_train_without_risk,
  check.names = FALSE
)

logistic_test <- data.frame(
  x_test_without_risk,
  check.names = FALSE
)


# -----------------------------------------------------------------------------
# Logistic-regression feature-matrix checkpoint
# -----------------------------------------------------------------------------

cat("Logistic-regression feature matrices\n")
cat(paste(rep("-", 72), collapse = ""), "\n", sep = "")

cat(
  "Without-risk training matrix: ",
  nrow(x_train_without_risk),
  " x ",
  ncol(x_train_without_risk),
  "\n",
  sep = ""
)

cat(
  "Without-risk test matrix:     ",
  nrow(x_test_without_risk),
  " x ",
  ncol(x_test_without_risk),
  "\n",
  sep = ""
)

cat(
  "With-risk training matrix:    ",
  nrow(x_train_with_risk),
  " x ",
  ncol(x_train_with_risk),
  "\n",
  sep = ""
)

cat(
  "With-risk test matrix:        ",
  nrow(x_test_with_risk),
  " x ",
  ncol(x_test_with_risk),
  "\n",
  sep = ""
)

cat("\n")

if (!identical(
  colnames(x_train_without_risk),
  colnames(x_test_without_risk)
)) {
  stop(
    "Without-risk training and test feature names do not match."
  )
}

if (!identical(
  colnames(x_train_with_risk),
  colnames(x_test_with_risk)
)) {
  stop(
    "With-risk training and test feature names do not match."
  )
}

if (nrow(x_train_without_risk) != 1178L) {
  stop("Unexpected without-risk training row count.")
}

if (nrow(x_test_without_risk) != 295L) {
  stop("Unexpected without-risk test row count.")
}

if (nrow(x_train_with_risk) != 1178L) {
  stop("Unexpected with-risk training row count.")
}

if (nrow(x_test_with_risk) != 295L) {
  stop("Unexpected with-risk test row count.")
}

cat("Feature-matrix structure: PASS\n")
cat("\n")

# -----------------------------------------------------------------------------
# Fit independent logistic-regression model
# -----------------------------------------------------------------------------

suppressPackageStartupMessages(
    library(pROC)
)
logistic_without_risk <- glm(
  current_subject_pass ~ .,
  data = logistic_train,
  family = binomial()
)
probabilities <- predict(
  logistic_without_risk,
  newdata = logistic_test,
  type = "response"
)
predictions <- ifelse(
  probabilities >= 0.5,
  1,
  0
)

predictions <- factor(
  predictions,
  levels = c(0,1)
)

actual <- factor(
  y_test,
  levels = c(0,1)
)
confusion <- table(
  Actual = actual,
  Predicted = predictions
)

print(confusion)
tn <- confusion["0","0"]
fp <- confusion["0","1"]
fn <- confusion["1","0"]
tp <- confusion["1","1"]

accuracy <- (tp + tn) / sum(confusion)

precision <- tp / (tp + fp)

recall <- tp / (tp + fn)

specificity <- tn / (tn + fp)

balanced_accuracy <- (
  recall +
  specificity
) / 2

f1 <- 2 * precision * recall /
(
  precision +
  recall
)
roc_result <- roc(
  response = as.numeric(
    as.character(actual)
  ),
  predictor = probabilities,
  levels = c(0,1),
  direction = "<",
  quiet = TRUE
)

roc_auc <- as.numeric(
  auc(roc_result)
)
cat("\n")
cat("Independent Logistic Regression — Without Risk\n")
cat(strrep("-",72),"\n")

print(confusion)

cat("\n")

cat(sprintf(
    "Accuracy          : %.7f\n",
    accuracy
))

cat(sprintf(
    "Balanced accuracy : %.7f\n",
    balanced_accuracy
))

cat(sprintf(
    "Precision         : %.7f\n",
    precision
))

cat(sprintf(
    "Recall            : %.7f\n",
    recall
))

cat(sprintf(
    "F1                : %.7f\n",
    f1
))

cat(sprintf(
    "ROC AUC           : %.7f\n",
    roc_auc
))
