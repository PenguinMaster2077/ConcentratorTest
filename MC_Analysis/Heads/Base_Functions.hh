#ifndef BASE_FUNCTIONS_HH
#define BASE_FUNCTIONS_HH
//CPP
#include <iostream>
#include <vector>
#include <filesystem>
#include <algorithm> // 引入 std::sort
//ROOT
#include <TFile.h>
#include <TVector3.h>
//JSAP
#include <JPSimOutput.hh>
//Self-Defined

std::vector<std::string> Get_All_Files(std::string Dir_Path)
{
    std::vector<std::string> Files;
    // Get all files
    for(const auto& entry: std::filesystem::directory_iterator(Dir_Path))
    {
        Files.push_back(entry.path().string());
    };

    // Rearrange Files
    std::sort(Files.begin(), Files.end());
    
    // Output
    return Files;
};

std::string Extract_File_Name(std::string Aba_Files)
{
    std::string File_Name = std::filesystem::path(Aba_Files).filename().string();

    // Output
    return File_Name;
}

std::vector<std::string> Extract_File_Names(const std::vector<std::string> &Abs_Files)
{
    std::vector<std::string> Files;
    for(const auto& file: Abs_Files)
    {
        Files.push_back(Extract_File_Name(file));
    };

    // 输出
    return Files;
};

std::string Extract_Name(std::string File_Name)
{
    std::string Name = std::filesystem::path(File_Name).stem().string();
    
    // Output
    return Name;
};

std::vector<std::string> Extract_Names(const std::vector<std::string> &Files)
{
    std::vector<std::string> Names;
    for(int index = 0; index < Files.size(); index++)
    {
        Names.push_back(Extract_Name(Files.at(index)));
    };

    // Output
    return Names;
}

std::vector<std::string> Collect_Info(std::string Name)
{
    std::vector<std::string> Head_Info;

    std::vector<size_t> positions;
    size_t pos = Name.find('_');  // 查找第一个'_'的位置
    
    while (pos != std::string::npos) {
        positions.push_back(pos);
        pos = Name.find('_', pos + 1);  // 查找下一个'_'的位置
    };
    
    // Get Infos
    std::string Distance = Name.substr(positions.at(0) - 1, 1);
    std::string Ball = Name.substr(positions.at(0) + 1, positions.at(1) - positions.at(0) - 3);
    std::string LED = Name.substr(positions.at(1) + 1, positions.at(2) - positions.at(1) - 1);
    std::string Angle = Name.substr(positions.at(2) + 1, positions.at(3) - positions.at(2) - 1);
    std::string Angle_Error = Name.substr(positions.at(3) + 1, 2);
    // Record
    Head_Info.push_back(Angle);
    Head_Info.push_back(Angle_Error);
    Head_Info.push_back(Distance);
    Head_Info.push_back(LED);
    Head_Info.push_back(Ball);
     
    // Output
    return Head_Info;
}

TVector3 Compute_Direction(Int_t index_1, Int_t index_2, std::vector<JPSimStepPoint_t> &steps)
{
    // Define Variables
    TVector3 direction(1, 0, 0);
    JPSimStepPoint_t step_before, step_after;
    // Get Info
    step_before = steps.at(index_1);
    step_after = steps.at(index_2);
    direction.SetXYZ(step_after.fX - step_before.fX, step_after.fY - step_before.fY, step_after.fZ - step_before.fZ);
    direction = direction.Unit();
    // Return Results
    return direction;
}

Double_t Compute_Reflectivity(Double_t CosTheta, Int_t Wavelength)
{
// Toy Code
    // Double_t Coeff[11] = {1.00015, -1.12392, 1.17405, 33.9181, -222.752, 704.243, -1337.0, 1595.46, -1174.01, 487.445, -87.4404};
    // Double_t res = 0;
    // for(int index = 0; index < 11; index++)
    // {
    //     res = res + Coeff[index] * pow(CosTheta, index);
    // };
// Get Correction Coefficients
    const Int_t len = 9;
    Double_t Coeff[len];
    if (Wavelength == 365)
    {
        Double_t temp[len] = {0.635511, 1.3213, 11.4057, -141.02, 510.633, -894.518, 821.959, -373.898, 64.1082};
        for (int i = 0; i < len; ++i) 
        {
            Coeff[i] = temp[i];
        };
    }
    else if (Wavelength == 415)
    {
        Double_t temp[len] = {0.618318, 1.44372, 13.4798, -157.288, 570.585, -1014.39, 953.135, -447.451, 80.558};
        for (int i = 0; i < len; ++i) 
        {
            Coeff[i] = temp[i];
        };
    }
    else if (Wavelength == 465)
    {
        Double_t temp[len] = {0.590706, 1.51497, 16.232, -185.54, 690.941, -1279.71, 1271.88, -645.97, 130.796};
        for (int i = 0; i < len; ++i) 
        {
            Coeff[i] = temp[i];
        };
    }
    else if (Wavelength == 480)
    {
        Double_t temp[len] = {0.644193, 1.62353, 4.96658, -87.6911, 313.736, -498.037, 368.978, -98.287, -5.1999};
        for (int i = 0; i < len; ++i) 
        {
            Coeff[i] = temp[i];
        };
    }
// Correction
    Double_t res = 0;
    for(int index = 0; index < len; index++)
    {
        res = res + Coeff[index] * pow(CosTheta, index);
    };
// Return
    return  res;
}

#endif