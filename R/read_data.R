pkgs <- c("sf", "tidyverse")
install.packages(pkgs[!pkgs %in% installed.packages()])

library(tidyverse)
seveneleven <- rio::import("data/seveneleven.json") %>%
    group_by(City, Town) %>%
    summarise(`7-11` = n())
hilife <- rio::import("data/hilife.json") %>%
    group_by(City, Town) %>%
    summarise(`hilife` = n())
okmart <- rio::import("data/okmart.json") %>%
    group_by(City, Town) %>%
    summarise(`okmart` = n())
familymart <- rio::import("data/familymart.json") %>%
    group_by(City, Town) %>%
    summarise(`familymart` = n())

cs_name <- c("7-11", "Hi Life", "OK", "FamilyMart")

complete <- seveneleven %>%
    full_join(hilife, by = c("City", "Town"), ) %>%
    full_join(okmart, by = c("City", "Town")) %>%
    full_join(familymart, by = c("City", "Town")) %>%
    mutate(across(`7-11`:familymart, replace_na, 0)) %>%
    rowwise() %>%
    mutate(dominance = cs_name[which.max(c(`7-11`, hilife, okmart, familymart))])

rio::export(complete, "data/domain_winner.csv")
