import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';


export default function Top_select({ method, method2, page, routed_p, routed_q }) {
  const router = useRouter();

  const [surveyOptions, setSurveyOptions] = useState([]);
  const [selectfile, setSelectfile] = useState(routed_p);
  const [selectedOptions, setSelectedOptions] = useState(routed_q);
  const [isSurveyOptionSelected, setIsSurveyOptionSelected] = useState(false);
  const [isSurveyqueSelected, setIsSurveyqueSelected] = useState(false);

  const [selectedQuestions, setSelectedQuestions] = useState(routed_q);
  const [questionOptions, setQuestionOptions] = useState([]);

  const handleSelectChange = async (selected) => {
    const newSelectedOptions = Array.isArray(selected) ? selected : [selected];
    setSelectedOptions(newSelectedOptions);
    setIsSurveyOptionSelected(newSelectedOptions.length > 0);

    if (newSelectedOptions.length > 0) {
      const selectedOption = newSelectedOptions[0];
      const questionOptionUrl = `http://115.68.193.117:9999/net/question-list?p_name=${selectedOption}`;
      const response = await axios.get(questionOptionUrl);
      const sur = response.data;
      const newArray = sur.map((item) => item.question_text);
      setQuestionOptions(newArray);
    }
  };

  useEffect(() => {
    method2(surveyOptions, selectedQuestions);
  }, [selectfile, selectedQuestions]);

  const handleQuestionChange = (selected) => {
    const newSelectedOptions = Array.isArray(selected) ? selected : [selected];
    setSelectedQuestions(newSelectedOptions);
    setIsSurveyqueSelected(newSelectedOptions.length > 0);
  };

  const dataselection = async () => {
    const surveyOptionsUrl = 'http://115.68.193.117:9999/net/file-list';
    const response = await axios.get(surveyOptionsUrl);
    const sur = response.data;
    const newArray = sur.map((item) => item.project_name);
    setSurveyOptions(newArray);
  };

  useEffect(() => {
    dataselection();
  }, []);

  const [datalocation, setDatalocation] = React.useState('mo');
  const handleChange = (event) => {
    setDatalocation(event.target.value);
  };

  const handleChange2 = (event, value) => {
    handleSelectChange(value);
    setSelectfile(value);
  };

  const handleChange3 = (event, value) => {
    handleQuestionChange(value);
  };

  const location = ['db', 'mo'];
  const data = 'mo';
  const top100Films = surveyOptions;

  return (
    <div>
      <div id="sedi">
        <div id="sedi2">
          <div className="onlyflex">
            <Autocomplete
              disablePortal
              id="combo-box-demo"
              options={top100Films}
              sx={{ width: 1340 }}
              onChange={(event, value) => handleChange2(event, value)}
              renderInput={(params) => <TextField {...params} label="데이터를 검색하거나 선택하세요." />}
            />
          </div>

          <div id="dash_options" className="onlyflex">
            <Autocomplete
              disablePortal
              id="combo-box-demo"
              options={questionOptions}
              sx={{ width: 1340 }}
              onChange={(event, value) => handleChange3(event, value)}
              renderInput={(params) => <TextField {...params} label="데이터를 검색하거나 선택하세요." />}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
