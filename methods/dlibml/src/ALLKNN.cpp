#include <dlib/graph_utils.h>
#include <mlpack/core.hpp>
#include <mlpack/core/util/timers.hpp>
#define BINDING_TYPE BINDING_TYPE_CLI
#include <mlpack/core/util/mlpack_main.hpp>

using namespace mlpack;
using namespace std;
using namespace dlib;

// Information about the program itself.
PROGRAM_INFO("K Nearest Neighbors",
    "This program will perform K Nearest Neighbors with the DLib-ml "
    "library.");

// Define our input parameters that this program will take.
PARAM_STRING_IN("reference_file", "File containing the reference dataset.",
    "r", "");
PARAM_INT_IN("k", "Value of K", "k", 0);

struct euclidean_distance
{
  euclidean_distance () : 
      lower(0),
      upper(std::numeric_limits<double>::infinity())
  {}

  euclidean_distance ( const double l, const double u ) :
        lower(l),
        upper(u)
  {}

   const double lower;
   const double upper;

   template <typename sample_type>
   double operator() ( const sample_type& a, const sample_type& b ) 
   const
         { 
            const double len = std::sqrt(length_squared(a-b));
            if (lower <= len && len <= upper)
              return len;
            else
              return std::numeric_limits<double>::infinity();
        }
};
void mlpackMain()
{
  // Get all the parameters.
  const string referenceFile = CLI::GetParam<string>("reference_file");

  size_t k = CLI::GetParam<int>("k");

  arma::mat referenceData;
  data::Load(referenceFile, referenceData, true);

  Log::Info << "Loaded reference data from '" << referenceFile << "' ("
      << referenceData.n_rows << " x " << referenceData.n_cols << ")." << endl;
  
 
  typedef matrix<double, 0, 1> sample_typ; 
  std::vector<sample_typ> samples_train;
  std::vector<sample_pair> out;
  
  sample_typ m;
  m.set_size(referenceData.n_rows);
  for (size_t i = 0; i < referenceData.n_cols; ++i)
  {
   for (size_t j = 0; j < referenceData.n_rows; ++j)
     m(j) = referenceData(j, i);

    samples_train.push_back(m);
  }

  Timer::Start("Nearest_Neighbors");
  
  find_k_nearest_neighbors(samples_train, euclidean_distance(), k, out);
  
  Timer::Stop("Nearest_Neighbors");
}
